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

import traceback

import requests

from firefly import domain
from ..resource_name_generator import ResourceNameGenerator


class HandleError(ResourceNameGenerator):
    _sns_client = None
    _serializer: domain.Serializer = None
    _slack_error_url: str = None
    _context: str = None

    def __call__(self, exception: Exception, event: dict, context):
        tb: list[str] = traceback.format_exception(etype=type(exception), value=exception, tb=exception.__traceback__)
        msg: str = self._build_message(exception, tb, event, context)

        if self._slack_error_url is not None:
            requests.post(self._slack_error_url, json={
                'text': msg,
            }, headers={
                'Content-Type': 'application/json',
            })

        self._sns_client.publish(
            TopicArn=self.alert_topic_arn(self._context),
            Message=self._serializer.serialize({
                'default': msg
            }),
            Subject=f'Error Executing {context.function_name}',
            MessageStructure='json'
        )

    def _build_message(self, exception: Exception, tb: list, event: dict, context):
        trace = "\n".join(tb)
        return f"""
Error Executing {context.function_name}

Got exception {exception.__class__.__name__}

Log Group: {context.log_group_name}
Log Stream: {context.log_stream_name}
Client Context: {context.client_context}

Event: {event}

Stack Trace:

{trace}
        """
