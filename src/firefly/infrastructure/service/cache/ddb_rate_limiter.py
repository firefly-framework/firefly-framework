from __future__ import annotations

from datetime import datetime, timedelta
from time import sleep

import firefly as ff
from botocore.exceptions import ClientError


class DdbRateLimiter(ff.RateLimiter):
    _ddb_client = None
    _ddb_table: str = None

    def acquire(self, key: str, max_concurrent: int, timeout: int = None) -> bool:
        mark = datetime.now()
        while True:
            try:
                self._ddb_client.update_item(
                    TableName=self._ddb_table,
                    Key={
                        'pk': {'S': key},
                        'sk': {'S': 'rate-limiter'}
                    },
                    UpdateExpression='ADD Rate :inc SET TimeToLive = :ttl',
                    ConditionExpression='attribute_not_exists(Rate) OR Rate < :limit',
                    ExpressionAttributeValues={
                        ':limit': {'N': str(max_concurrent)},
                        ':inc': {'N': '1'},
                        ':ttl': {'N': str(int((datetime.now() + timedelta(minutes=5)).timestamp()))}
                    }
                )
                return True
            except ClientError as e:
                if 'ConditionalCheckFailedException' in str(e):
                    print(e)
                    if timeout is not None and (datetime.now() - mark).seconds >= timeout:
                        raise TimeoutError(f'Could not acquire mutex for key: {key}')
                    sleep(1)
                else:
                    raise e

    def release(self, key: str):
        self._ddb_client.update_item(
            TableName=self._ddb_table,
            Key={
                'pk': {'S': key},
                'sk': {'S': 'rate-limiter'}
            },
            UpdateExpression='ADD Rate :dec',
            ConditionExpression='Rate > :limit',
            ExpressionAttributeValues={
                ':limit': {'N': '0'},
                ':dec': {'N': '-1'},
            }
        )
