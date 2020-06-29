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

from datetime import datetime
from pprint import pprint

import firefly as ff


class Coordinates(ff.ValueObject):
    latitude: float = ff.required()
    longitude: float = ff.required()


class Activity(ff.AggregateRoot):
    id: str = ff.id_()
    email: str = ff.optional(validators=[ff.IsValidEmail()])
    registrant: str = ff.optional(index=True)
    member_id: str = ff.optional(index=True)
    manually_created: bool = ff.optional(default=False, index=True)
    local_start_time: datetime = ff.required(index=True)
    distance: float = ff.required()
    duration: float = ff.required()
    elevation_gain: float = ff.optional(float)
    starting_coordinates: Coordinates = ff.optional()
    ending_coordinates: Coordinates = ff.optional()

    distributed_event: str = ff.optional(index=True)
    course: str = ff.optional(index=True)
    segment: str = ff.optional()
    created_on: datetime = ff.now(index=True)


a = Activity(
    email='jd@pwrlab.com',
    registrant='registrant-id',
    member_id='member-id',
    manually_created=True,
    local_start_time=datetime.now(),
    distance=5000,
    duration=3600,
    distributed_event='de-id',
    course='course-id'
)

pprint(Activity.get_dto_schema())
