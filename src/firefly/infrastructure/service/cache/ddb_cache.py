from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import firefly as ff
from dynamodb_json import json_util


class DdbCache(ff.Cache):
    _ddb_client = None
    _ddb_table: str = None

    def set(self, key: str, value: Any, ttl: int = None, **kwargs) -> Any:
        if '.' in str(key):
            return self._set_property(key, value)
        else:
            return self._set_item(key, value, ttl)

    def get(self, key: str, **kwargs) -> Any:
        response = self._ddb_client.get_item(
            TableName=self._ddb_table,
            Key=json_util.dumps({
                'pk': key,
                'sk': 'CacheItem',
            }, as_dict=True),
        )

        if 'Item' in response:
            return json_util.loads(response['Item'], as_dict=True)['value']

        return None

    def delete(self, key: str, **kwargs) -> Any:
        response = self._ddb_client.delete_item(
            TableName=self._ddb_table,
            Key=json_util.dumps({
                'pk': key,
                'sk': 'CacheItem',
            }, as_dict=True),
            ReturnValues='ALL_OLD'
        )

        if 'Attributes' in response:
            return json_util.loads(response['Attributes'], as_dict=True)['value']

        return None

    def clear(self):
        raise NotImplemented('DdbCache does not support clear()')

    def increment(self, key: str, amount: int = 1, **kwargs) -> Any:
        k = str(key).split('.').pop(0)
        attribute_names, path = self._process_path(key)

        params = {
            'TableName': self._ddb_table,
            'Key': json_util.dumps({
                'pk': k,
                'sk': 'CacheItem',
            }, as_dict=True),
            'UpdateExpression': f'SET {path} = {path} + :inc',
            'ExpressionAttributeValues': json_util.dumps({
                ':inc': amount,
            }, as_dict=True),
            'ExpressionAttributeNames': attribute_names,
            'ReturnValues': 'ALL_NEW',
        }

        ret = self._ddb_client.update_item(**params)
        if 'Attributes' in ret:
            return json_util.loads(ret['Attributes'], as_dict=True)['value']

        return None

    def decrement(self, key: str, amount: int = 1, **kwargs) -> Any:
        return self.increment(str(key), amount=(-amount))

    def add(self, key: str, value: Any, **kwargs) -> Any:
        k = key.split('.').pop(0)
        attribute_names = {f'#val_{i}': v for i, v in enumerate(key.split('.'))}
        attribute_names['#val_0'] = 'value'
        path = '.'.join([f'#val_{i}' for i, _ in enumerate(key.split('.'))])

        params = {
            'TableName': self._ddb_table,
            'Key': json_util.dumps({
                'pk': k,
                'sk': 'CacheItem',
            }, as_dict=True),
            'UpdateExpression': f'SET {path} = list_append(if_not_exists({path}, :empty_list), :val)',
            'ExpressionAttributeValues': json_util.dumps({
                ':val': [value],
                ':empty_list': [],
            }, as_dict=True),
            'ExpressionAttributeNames': attribute_names,
            'ReturnValues': 'ALL_NEW',
        }

        ret = self._ddb_client.update_item(**params)
        if 'Attributes' in ret:
            return json_util.loads(ret['Attributes'], as_dict=True)['value']

        return None

    def remove(self, key: str, value: Any, **kwargs) -> Any:
        parts = key.split('.')
        item = self.get(parts.pop(0))
        if item is None:
            return None

        while len(parts) > 0:
            item = item[parts.pop(0)]
        index = item.index(value)

        if index is None:
            return None

        k = key.split('.').pop(0)
        attribute_names, path = self._process_path(key)

        params = {
            'TableName': self._ddb_table,
            'Key': json_util.dumps({
                'pk': k,
                'sk': 'CacheItem',
            }, as_dict=True),
            'UpdateExpression': f'REMOVE {path}[{index}]',
            'ExpressionAttributeNames': attribute_names,
            'ReturnValues': 'ALL_NEW',
        }

        ret = self._ddb_client.update_item(**params)
        if 'Attributes' in ret:
            return json_util.loads(ret['Attributes'], as_dict=True)['value']

        return None

    def _set_property(self, key: str, value: Any):
        k = key.split('.').pop(0)
        attribute_names = {f'#val_{i}': v for i, v in enumerate(key.split('.'))}
        attribute_names['#val_0'] = 'value'
        path = '.'.join([f'#val_{i}' for i, _ in enumerate(key.split('.'))])

        params = {
            'TableName': self._ddb_table,
            'Key': json_util.dumps({
                'pk': k,
                'sk': 'CacheItem',
            }, as_dict=True),
            'UpdateExpression': f'SET {path} = :val',
            'ExpressionAttributeValues': json_util.dumps({
                ':val': value,
            }, as_dict=True),
            'ExpressionAttributeNames': attribute_names,
            'ReturnValues': 'ALL_NEW',
        }

        ret = self._ddb_client.update_item(**params)
        if 'Attributes' in ret:
            return json_util.loads(ret['Attributes'], as_dict=True)['value']

        return None

    def _set_item(self, key: str, value: Any, ttl: int = None, if_not_exists: bool = False):
        item = {
            'pk': key,
            'sk': 'CacheItem',
            'value': value,
        }

        if ttl is not None:
            item['TimeToLive'] = (datetime.now() + timedelta(seconds=ttl)).timestamp()

        params = {
            'TableName': self._ddb_table,
            'Item': json_util.dumps(item, as_dict=True),
            'ReturnValues': 'ALL_OLD',
        }

        if if_not_exists is True:
            params['KeyConditionExpression'] = 'if_not_exists(pk)'

        ret = self._ddb_client.put_item(**params)
        if 'Attributes' in ret:
            return json_util.loads(ret['Attributes'], as_dict=True)

        return None

    def _process_path(self, key: str):
        attribute_names = {f'#val_{i}': v for i, v in enumerate(key.split('.'))}
        attribute_names['#val_0'] = 'value'
        path = '.'.join([f'#val_{i}' for i, _ in enumerate(key.split('.'))])

        return attribute_names, path
