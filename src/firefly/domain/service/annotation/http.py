from __future__ import annotations

import uuid

import firefly.domain as ffd

from .framework_annotation import FrameworkAnnotation


class Http(FrameworkAnnotation):
    def name(self) -> str:
        return '__ff_port'

    def __call__(self, path: str = None, method: str = 'get', target: type = None, cors: bool = False):
        kwargs = locals()
        del kwargs['self']
        if '__class__' in kwargs:
            del kwargs['__class__']
        kwargs['id_'] = str(uuid.uuid1())
        kwargs['endpoint'] = ffd.HttpEndpoint(method, path)
        del kwargs['method']
        del kwargs['path']
        cmd = ffd.RegisterHttpPort(**kwargs)
        return super().__call__(child_callback=self._cb, command=cmd)

    def _cb(self, parent: object, child: object):
        parent_cmd = getattr(parent, self.name())
        for cmd in getattr(child, self.name()):
            cmd['command'].parent = parent_cmd[0]['command'].id_

    @staticmethod
    def _callback(cls, kwargs):
        kwargs['command'].decorated = cls
        return kwargs


http = Http()
