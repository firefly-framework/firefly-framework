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
    path: str = None
    method: str = None

    private: bool = None
    authorizer: object = None

    def __init__(self, target: object, for_: ffd.Service, **kwargs):
        """
        :param cors:
            cors=True

            is the equivalent of

            cors={
                origin: '*',
                allow_credentials: False,
                headers: ('Content-Type', 'Authorization'),
            }
        :type cors: Boolean or dict
        """
        if kwargs['method'] is not None and kwargs['path'] is not None:
            self.method = kwargs['method'].upper()
            self.path = f'/{kwargs["path"].lstrip("/")}'
        if 'cors' in kwargs:
            self.cors = kwargs['cors'] if kwargs['cors'] is not True else self.DEFAULT_CORS

        super().__init__(id_=self._generate_id(), target=target, service=for_)

    def get_routes(self):
        return [{
            'method': self.method,
            'path': self.path,
            'cors': self.cors,
            'port': self,
        }]

    def extend(self, port: HttpPort):
        super().extend(port)

        for prop in ('cors', 'method'):
            if getattr(port, prop) is not None and getattr(self, prop) is None:
                setattr(self, prop, getattr(port, prop))

        if port.path is not None:
            self.path = f'{port.path.rstrip("/")}{self.path}'
            self.id = self._generate_id()

    def _generate_id(self):
        return f'{self.method} {self.path}'
