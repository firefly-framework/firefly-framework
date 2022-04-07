#  Copyright (c) 2020 JD Williams
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

import gzip
import uuid

import firefly as ff
import firefly_aws.domain as awsd
from botocore.exceptions import ClientError


class BotoS3Service(awsd.S3Service, ff.LoggerAware):
    _configuration: ff.Configuration = None
    _s3_client = None
    _bucket: str = None

    def store_download(self, data: str, extension: str = None, file_name: str = None, apply_compression: bool = True):
        key = file_name if file_name is not None else str(uuid.uuid4())
        content_encoding = None
        if extension is not None:
            key += f".{extension}"

        if apply_compression:
            data = gzip.compress(data.encode('utf-8'))
            key += '.gz'
            content_encoding = 'gzip'

        key = f'/tmp/{key}'

        params = {
            'Body': data,
            'Bucket': self._bucket,
            'Key': key,
        }
        if content_encoding is not None:
            params['Metadata'] = {
                'ContentEncoding': content_encoding,
            }

        self._s3_client.put_object(**params)

        return self._s3_client.generate_presigned_url(
            'get_object', Params={'Bucket': self._bucket, 'Key': key}
        )
