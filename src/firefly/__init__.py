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

# __pragma__('skip')
from typing import Tuple, List, Union, Type

from .domain import *

EventList = Union[Event, Tuple[str, Union[dict, object]], List[Union[Event, Tuple[str, Union[dict, object]]]]]
TypeOfMessage = Union[str, Type[Message]]
TypeOfCommand = Union[str, Type[Command]]
TypeOfEvent = Union[str, Type[Event]]
TypeOfQuery = Union[str, Type[Query]]
# __pragma__('noskip')
# __pragma__ ('ecom')
"""?
from firefly.presentation.web.polyfills import Entity, AggregateRoot, Message, Command, Query, Event, ValueObject
from firefly.domain.entity.entity import required, optional, id_, now, list_, dict_, today, hidden
from firefly.domain.entity.validation.validators import IsType, HasLength, Matches, IsValidEmail, IsOneOf, IsDatetime, IsNumeric, IsFloat, IsInt, IsValidUrl
from firefly.domain.error import MissingArgument, FrameworkError
from firefly.domain.service.entity.validator import Validator
from firefly.domain.service.messaging import SystemBus, Middleware, CommandBus, EventBus, QueryBus, MessageFactory
?"""
# __pragma__ ('noecom')
