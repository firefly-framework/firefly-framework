from __future__ import annotations

import json

import firefly.domain as ffd


class DefaultSerializer(ffd.Serializer):
    def serialize(self, data):
        return json.dumps(data)

    def deserialize(self, data):
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            raise ffd.InvalidArgument('Could not deserialize data')
