from __future__ import annotations

from datetime import date, datetime
from typing import Tuple, List

import firefly as ff
from botocore.exceptions import ClientError


class S3FileSystem(ff.FileSystem, ff.LoggerAware):
    _s3_client = None
    _bucket: str = None

    def read(self, file_name: str) -> ff.File:
        bucket, file_name = self._parse_file_path(file_name)
        try:
            response = self._s3_client.get_object(Bucket=bucket, Key=file_name)
        except self._s3_client.exceptions.NoSuchKey:
            raise ff.NoSuchFile()

        content = response['Body'].read()
        try:
            content = content.decode('utf-8')
        except UnicodeDecodeError:
            pass

        return ff.File(
            name=file_name,
            content=content,
            content_type=response.get('ContentType', None)
        )

    def write(self, file: ff.File, path: str = None):
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

    def filter(self, path: str, fields: list, criteria: ff.BinaryOp):
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
