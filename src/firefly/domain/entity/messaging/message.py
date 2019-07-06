from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..entity import *


@dataclass()
class Message(Entity):
    _id: str = pk()
    _headers: dict = dict_()
    _body: Any = None

    def __init__(self, body: object = None, headers: dict = None):
        self._body = body
        self._headers = headers or {}
        self._id = self._headers['_id'] if '_id' in self._headers else str(uuid.uuid1())
        self.header('_id', self._id)

    def to_dict(self) -> dict:
        return {
            'headers': self._headers,
            'body': self._body
        }

    def header(self, key: str = None, value: object = None):
        if value is not None:
            self._headers[key] = value
            return self
        else:
            return self._headers.get(key)

    def get(self, key: str = None, default: Any = None):
        return self._headers[key] if key in self._headers else default

    def headers(self, data: dict = None):
        if data is not None:
            self._headers = data
            return self
        else:
            return self._headers

    def unset(self, key: str):
        try:
            del self._headers[key]
        except KeyError:
            pass

    def body(self, data: object = None):
        if data is not None:
            self._body = data
            return self
        else:
            return self._body

    def merge(self, message):
        self._headers.update(message.headers())
        self.body(message.body())

        return self

    def resolve(self, key: str):
        dic = {
            'headers': self._headers,
            'body': self._body
        }

        parts = key.split('.')
        while len(parts) > 0:
            key = parts.pop(0)
            if key in dic:
                dic = dic[key]
            else:
                return False

        return dic

    def set_path(self, key: str, value):
        parts = key.split('.')
        first = parts.pop(0)

        dic = self._headers if first == 'headers' else self._body
        while len(parts) > 0:
            key = parts.pop(0)
            if key in dic:
                if len(parts) > 0:
                    dic = dic[key]
                else:
                    dic[key] = value
            else:
                if len(parts) > 0:
                    dic[key] = {}
                    dic = dic[key]
                else:
                    dic[key] = value

        return self
