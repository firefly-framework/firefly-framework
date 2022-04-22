#  Copyright (c) 2019 JD Williams
#
#  This file is part of Firefly, a Python SOA framework built by JD Williams. Firefly is free software; you can
#  redistribute it and/or modify it under the terms of the GNU General Public License as published by the
#  Free Software Foundation; either version 3 of the License, or (at your option) any later version.
#
#  Firefly is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
#  implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
#  Public License for more details. You should have received a copy of the GNU Lesser General Public
#  License along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#  You should have received a copy of the GNU General Public License along with Firefly. If not, see
#  <http://www.gnu.org/licenses/>.

from __future__ import annotations

from datetime import date, datetime
from typing import Tuple, List

import firefly.domain as ffd
from botocore.exceptions import ClientError


class S3FileSystem(ffd.FileSystem, ffd.LoggerAware):
    _s3_client = None
    _bucket: str = None

    def read(self, file_name: str) -> ffd.File:
        bucket, file_name = self._parse_file_path(file_name)
        try:
            response = self._s3_client.get_object(Bucket=bucket, Key=file_name)
        except self._s3_client.exceptions.NoSuchKey:
            raise ffd.NoSuchFile()

        content = response['Body'].read()
        try:
            content = content.decode('utf-8')
        except UnicodeDecodeError:
            pass

        return ffd.File(
            name=file_name,
            content=content,
            content_type=response.get('ContentType', None)
        )

    def write(self, file: ffd.File, path: str = None):
        path = '/'.join([(path or '').rstrip('/'), file.name])
        bucket, file_name = self._parse_file_path(path)
        params = {}
        if file.content_type is not None:
            params['ContentType'] = file.content_type
        self._s3_client.put_object(
            Bucket=bucket,
            Key=file_name,
            Body=file.content,
            **params
        )

    def list(self, path: str) -> List[Tuple[str, dict]]:
        bucket, file_name = self._parse_file_path(path)
        params = {'Bucket': bucket, 'Prefix': file_name}
        ret = []

        while True:
            response = self._s3_client.list_objects_v2(**params)
            if 'Contents' in response:
                for item in response['Contents']:
                    ret.append((f"{bucket}/{item['Key']}", {
                        'size': item['Size'],
                        'last_modified': item['LastModified'],
                    }))
            if response['IsTruncated'] and 'NextContinuationToken' in response:
                params['ContinuationToken'] = response['NextContinuationToken']
            else:
                break

        return ret

    def filter(self, path: str, fields: list, criteria: ffd.SearchCriteria):
        bucket, file_name = self._parse_file_path(path)

        sql = f"select {', '.join(fields)} from s3object s"
        if criteria is not None:
            where, params = criteria.to_sql(prefix='s')
            for k, v in params.items():
                if isinstance(v, str):
                    where = where.replace(f':{k}', f"'{v}'")
                elif isinstance(v, (datetime, date)):
                    format_ = "y-MM-dd''T''H:m:ss" if isinstance(v, datetime) else 'y-MM-dd'
                    where = where.replace(f':{k}', f"TO_TIMESTAMP('{v.isoformat()}', '{format_}')")
                else:
                    where = where.replace(f':{k}', str(v))
            sql += f' where {where}'

        compression = 'NONE'
        fn = file_name.lower()
        if fn.endswith('.bz2'):
            compression = 'BZIP2'
        elif fn.endswith('.gz'):
            compression = 'GZIP'

        input_serialization = {
            'CompressionType': compression
        }
        if '.parquet' in fn:
            input_serialization['Parquet'] = {}
        elif '.json' in fn:
            input_serialization['JSON'] = {
                'Type': 'DOCUMENT',
            }
        elif '.csv' in fn:
            input_serialization['CSV'] = {
                'FileHeaderInfo': 'Use',
            }

        try:
            response = self._s3_client.select_object_content(
                Bucket=bucket,
                Key=file_name,
                InputSerialization=input_serialization,
                OutputSerialization={'JSON': {}},
                Expression=sql,
                ExpressionType='SQL'
            )
        except ClientError as e:
            print(e)
            return ''

        ret = '['
        for event in response['Payload']:
            if 'Records' in event:
                ret += event['Records']['Payload'].decode('utf-8').replace("\n", ",").replace('\\r', '')

        return ret.rstrip(',') + ']'

    def _parse_file_path(self, path: str):
        parts = path.lstrip('/').split('/')
        bucket = parts.pop(0)
        file_name = '/'.join(parts)

        return bucket, file_name
