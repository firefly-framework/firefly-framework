from __future__ import annotations

import uuid

import firefly.domain as ffd


class StoreLargePayloadsInS3:
    _s3_client = None
    _serializer: ffd.Serializer = None
    _bucket: str = None

    def __call__(self, payload: str, name: str, context: str, type_: str, id_: str):
        if len(payload) > 64_000:
            key = f'tmp/{str(uuid.uuid1())}.json'
            self._s3_client.put_object(
                Body=payload,
                Bucket=self._bucket,
                Key=key
            )
            return self._serializer.serialize({
                'PAYLOAD_KEY': key,
                '_name': name,
                '_type': type_,
                '_context': context,
                '_id': id_,
            })

        return payload
