from __future__ import annotations

from datetime import datetime, timedelta
from time import sleep

import firefly as ff
from botocore.exceptions import ClientError


class DdbMutex(ff.Mutex):
    _ddb_client = None
    _ddb_table: str = None

    def acquire(self, key: str, timeout: int = None) -> bool:
        mark = datetime.now()
        while True:
            try:
                self._ddb_client.put_item(
                    TableName=self._ddb_table,
                    Item={
                        'pk': {'S': key},
                        'sk': {'S': 'mutex'},
                        'TimeToLive': {'N': str(round((datetime.now() + timedelta(seconds=(60 * 15))).timestamp()))},
                    },
                    ConditionExpression=f'attribute_not_exists(pk)'
                )
                return True
            except ClientError as e:
                if 'ConditionalCheckFailedException' in str(e):
                    if timeout is not None and (datetime.now() - mark).seconds >= timeout:
                        raise TimeoutError(f'Could not acquire mutex for key: {key}')
                    sleep(1)
                else:
                    raise e

    def release(self, key: str):
        try:
            self._ddb_client.delete_item(
                TableName=self._ddb_table,
                Key={
                    'pk': {'S': key},
                    'sk': {'S': 'mutex'},
                }
            )
            return True
        except ClientError:
            return False
