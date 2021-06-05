#  Copyright (c) 2019 JD Williams
#
#  This file is part of Firefly, a Python SOA framework built by JD Williams. Firefly is free software; you can
#  redistribute it and/or modify it under the terms of the GNU General Public License as published by the
#  Free Software Foundation; either version 3 of the License, or (at your option) any later version.
#
#  Firefly is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
#  implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
#  Public License for more details. You should have received a copy of the GNU Lesser General Public
#  License along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#  You should have received a copy of the GNU General Public License along with Firefly. If not, see
#  <http://www.gnu.org/licenses/>.

from __future__ import annotations

import inspect
import json
from datetime import datetime, date, time
from json import JSONEncoder
from pprint import pprint

import firefly.domain as ffd
import firefly_di as di


class FireflyEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, ffd.ValueObject):
            return o.to_dict()
        elif inspect.isclass(o) and issubclass(o, ffd.Entity):
            return f'{o.get_class_context()}.{o.__name__}'
        elif isinstance(o, (di.Container, ffd.Empty)):
            return None
        elif isinstance(o, (datetime, date, time)):
            return o.isoformat()
        elif not inspect.isclass(o) and isinstance(o, ffd.Message):
            try:
                dic = o.to_dict()
                dic['_name'] = o.__class__.__name__
                t = 'event'
                if isinstance(o, ffd.Command):
                    t = 'command'
                elif isinstance(o, ffd.Query):
                    t = 'query'
                dic['_type'] = t
                return dic
            except AttributeError:
                pass

        return JSONEncoder.default(self, o)


class JsonSerializer(ffd.Serializer):
    _message_factory: ffd.MessageFactory = None

    def serialize(self, data):
        return json.dumps(data, cls=FireflyEncoder, skipkeys=True)

    def deserialize(self, data):
        try:
            if isinstance(data, (str, bytes, bytearray)):
                ret = json.loads(data)
            else:
                ret = data
        except json.JSONDecodeError:
            raise ffd.InvalidArgument('Could not deserialize data')

        if isinstance(ret, dict) and '_name' in ret:
            fqn = f'{ret["_context"]}.{ret["_name"]}'
            t = ffd.load_class(fqn)
            if t is None:
                args = [fqn]
                if ret['_type'] == 'query':
                    args.append(None)
                args.append(ret)
                return getattr(self._message_factory, ret['_type'])(*args)
            return t(**ffd.build_argument_list(ret, t))

        return ret
