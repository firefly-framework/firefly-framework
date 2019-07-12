from __future__ import annotations

import json
from dataclasses import fields
from json import JSONDecodeError
from typing import Union, TypeVar, Type

import firefly.domain as ffd

from .port import Port
from ..messaging.message import Message

M = TypeVar('M', bound=Message)


class HttpPort(Port):
    DEFAULT_CORS = {
        'origin': '*',
        'allow_credentials': False,
        'headers': ('Content-Type', 'Authorization'),
    }

    cors: Union[bool, dict] = False
    endpoint: ffd.HttpEndpoint = None

    private: bool = None
    authorizer: object = None

    def __init__(self, target: Type[M], config: dict, endpoint: ffd.HttpEndpoint, cors: Union[bool, dict] = False):
        super().__init__(target, config)
        self.endpoint = endpoint
        self.cors = cors

    def _transform_input(self, headers: dict, body: str, **kwargs) -> ffd.Message:
        params = {}
        try:
            params.update(json.loads(body))
        except JSONDecodeError:
            pass

        message = self.target(**params)
        message.headers['http'] = headers
        message.headers['origin'] = 'http'
        return message

    def _transform_output(self, message: ffd.Message):
        return message
