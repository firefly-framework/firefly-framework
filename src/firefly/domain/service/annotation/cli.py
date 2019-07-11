from __future__ import annotations

import uuid

import inflection

from .framework_annotation import FrameworkAnnotation
import firefly.domain as ffd


class Cli(FrameworkAnnotation):
    def name(self) -> str:
        return '__ff_port'

    def __call__(self, name: str = None, description: str = None, target: object = None, alias: dict = None,
                 help_: dict = None, device_id: str = None):
        kwargs = locals()
        del kwargs['self']
        if '__class__' in kwargs:
            del kwargs['__class__']
        kwargs['id_'] = str(uuid.uuid1())
        cmd = ffd.RegisterCliPort(**kwargs)
        return super().__call__(child_callback=self._cb, command=cmd)

    def _cb(self, parent: object, child: object):
        parent_cmd = getattr(parent, self.name())
        for cmd in getattr(child, self.name()):
            cmd['command'].parent = parent_cmd[0]['command'].id_

    @staticmethod
    def _callback(cls, kwargs):
        if kwargs['command'].name is None:
            kwargs['command'].name = inflection.dasherize(inflection.underscore(cls.__name__))
        kwargs['command'].decorated = cls
        return kwargs


cli = Cli()
