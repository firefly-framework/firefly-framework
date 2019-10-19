from __future__ import annotations

import json
from json import JSONEncoder

import firefly.domain as ffd
import firefly_di as di


class FireflyEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, ffd.Entity):
            return o.to_dict()
        elif isinstance(o, di.Container):
            return None
        elif isinstance(o, ffd.Message):
            dic = o.to_dict()
            dic['_name'] = o.__class__.__name__
            t = 'event'
            if isinstance(o, ffd.Command):
                t = 'command'
            elif isinstance(o, ffd.Query):
                t = 'query'
            dic['_type'] = t
            return dic

        return JSONEncoder.default(self, o)


class DefaultSerializer(ffd.Serializer):
    _message_factory: ffd.MessageFactory = None

    def serialize(self, data):
        return json.dumps(data, cls=FireflyEncoder)

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
