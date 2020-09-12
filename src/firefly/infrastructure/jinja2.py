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
from dataclasses import fields

import firefly.domain as ffd
from firefly.infrastructure.repository.rdb_repository import Index


def is_attribute(x):
    return isinstance(x, (ffd.Attr, ffd.AttributeString))


def is_criteria(x):
    return isinstance(x, ffd.BinaryOp)


def id_field(x):
    for field_ in fields(x):
        if 'id' in field_.metadata:
            return field_


def indexes(entity):
    ret = []
    for field_ in fields(entity):
        if 'index' in field_.metadata:
            if field_.metadata['index'] is True:
                ret.append(Index(columns=[field_.name], unique=field_.metadata.get('unique', False) is True))
            elif isinstance(field_.metadata['index'], str):
                name = field_.metadata['index']
                idx = next(filter(lambda i: i.name == name, ret))
                if not idx:
                    ret.append(Index(columns=[field_.name], unique=field_.metadata.get('unique', False) is True))
                else:
                    idx.columns.append(field_.name)
                    if field_.metadata.get('unique', False) is True and idx.unique is False:
                        idx.unique = True

    return ret
