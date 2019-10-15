from __future__ import annotations

import json

import firefly.domain as ffd


class DefaultSerializer(ffd.Serializer):
    _message_factory: ffd.MessageFactory = None

    def serialize(self, data):
        if isinstance(data, ffd.Message):
            dic = data.to_dict()
            dic['_name'] = data.__class__.__name__
            t = 'event'
            if isinstance(data, ffd.Command):
                t = 'command'
            elif isinstance(data, ffd.Query):
                t = 'query'
            dic['_type'] = t
            return json.dumps(dic)

        return json.dumps(data)

    def deserialize(self, data):
        try:
            ret = json.loads(data)
        except json.JSONDecodeError:
            raise ffd.InvalidArgument('Could not deserialize data')

        if isinstance(ret, dict) and '_name' in ret:
            fqn = f'{ret["_context"]}.{ret["_name"]}'
            t = ffd.load_class(fqn)
            if t is None:
                return getattr(self._message_factory, ret['_type'])(fqn, ret)
            return t(**ffd.build_argument_list(ret, t))

        return ret
