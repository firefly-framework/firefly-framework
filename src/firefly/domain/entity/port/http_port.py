from __future__ import annotations

from typing import Union

import firefly.domain as ffd

from .port import Port


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

    def _transform_input(self, headers: dict, body: str, **kwargs) -> ffd.Message:
        return ffd.HttpMessage(http_headers=headers, body=body)

    def _transform_output(self, message: ffd.Message):
        pass
