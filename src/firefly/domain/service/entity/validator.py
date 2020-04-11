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

from firefly.domain.entity.entity import Entity

# __pragma__('skip')
from dataclasses import Field
from typing import Type
# __pragma__('noskip')
# __pragma__ ('ecom')
"""?
from firefly.presentation.web.polyfills import Field, Type
?"""
# __pragma__ ('noecom')


class Validator:
    def validate(self, dto: dict, against: Type[Entity]):
        validations = {}
        for k in dir(against):
            v = getattr(against, k)
            if isinstance(v, Field):
                validators = self._parse_field(v)
            elif isinstance(v, dict):
                validators = self._parse_dict(v)
            else:
                continue
            if validators['validators'] is not None:
                validations[k] = validators

        error_messages = {}
        count = 0
        for k, validators in validations.items():
            if (k not in dto or dto[k] is None) and not validators['required']:
                continue

            for validator in validators['validators']:
                if not getattr(validator, '__call__')(dto[k], dto):
                    if k not in error_messages:
                        error_messages[k] = []
                    error_messages[k].append(validator.message.format(k))
                    count += 1

        return {
            'count': count,
            'errors': error_messages,
        }

    @staticmethod
    def _parse_field(value: Field):
        ret = {
            'required': True,
            'validators': None
        }

        if 'required' in value.metadata and not value.metadata['required']:
            ret['required'] = False

        if 'validators' in value.metadata:
            ret['validators'] = value.metadata['validators']

        return ret

    @staticmethod
    def _parse_dict(value: dict):
        ret = {
            'required': True,
            'validators': None
        }

        if isinstance(value, dict) and 'metadata' in value:
            if 'required' in value['metadata'] and not value['metadata']['required']:
                ret['required'] = False

            if 'validators' in value['metadata']:
                ret['validators'] = value['metadata']['validators']

        return ret
