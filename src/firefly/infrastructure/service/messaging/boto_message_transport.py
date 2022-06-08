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

import uuid
from typing import Any, Union

from botocore.exceptions import ClientError
from devtools import debug

import firefly as ff
from firefly.domain.service.resource_name_generator import ResourceNameGenerator
from firefly.domain.service.messaging.message_transport import MessageTransport


class BotoMessageTransport(MessageTransport, ResourceNameGenerator, ff.LoggerAware):
    _serializer: ff.Serializer = None
    _kernel: ff.Kernel = None
    _store_large_payloads_in_s3: ff.StoreLargePayloadsInS3 = None
    _load_payload: ff.LoadPayload = None
    _lambda_client = None
    _sns_client = None
    _sqs_resource = None
    _s3_client = None
    _bucket: str = None
    _context: str = None

    def dispatch(self, event: ff.Event) -> None:
        try:
            if hasattr(event, '_memory'):
                self._enqueue_message(event, context=self._context)
            else:
                self._sns_client.publish(
                    TopicArn=self.topic_arn(event.get_context()),
                    Message=self._store_large_payloads_in_s3(
                        self._serializer.serialize(event),
                        name=event.__class__.__name__,
                        type_='command' if isinstance(event, ff.Command) else 'event',
                        context=event.get_context(),
                        id_=getattr(event, '_id', str(uuid.uuid4()))
                    ),
                    MessageAttributes={
                        '_name': {
                            'DataType': 'String',
                            'StringValue': event.__class__.__name__,
                        },
                        '_type': {
                            'DataType': 'String',
                            'StringValue': 'event'
                        },
                        '_context': {
                            'DataType': 'String',
                            'StringValue': event.get_context()
                        },
                    }
                )
        except ClientError as e:
            raise ff.MessageBusError(str(e))

    def invoke(self, command: ff.Command) -> Any:
        return self._invoke_lambda(command)

    def request(self, query: ff.Query) -> Any:
        return self._invoke_lambda(query)

    def _invoke_lambda(self, message: Union[ff.Command, ff.Query]):
        if hasattr(message, '_async') and getattr(message, '_async') is True:
            return self._enqueue_message(message)

        if message.get_context() == self._context:
            self.info("We're in the same context, running code locally...")
            for app in self._kernel.get_application_services():
                if app.__name__ == str(message).split('.').pop():
                    app = self._kernel.build(app)
                    return app(**ff.build_argument_list(message.to_dict(), app))

        try:
            response = self._lambda_client.invoke(
                FunctionName=self.lambda_function_name(message.get_context(), type_="sync"),
                InvocationType='RequestResponse',
                LogType='None',
                Payload=self._serializer.serialize(message)
            )
        except ClientError as e:
            raise ff.MessageBusError(str(e))

        ret = self._serializer.deserialize(response['Payload'].read().decode('utf-8'))
        if isinstance(ret, dict) and 'PAYLOAD_KEY' in ret:
            ret = self._load_payload(ret['PAYLOAD_KEY'])

        return ret

    def _enqueue_message(self, message: ff.Message, context: str = None):
        memory = None
        if hasattr(message, '_memory'):
            memory = getattr(message, '_memory')
        queue = self._sqs_resource.get_queue_by_name(
            QueueName=self.queue_name(context or message.get_context(), memory=memory)
        )
        queue.send_message(MessageBody=self._store_large_payloads_in_s3(
            self._serializer.serialize(message),
            name=message.__class__.__name__,
            type_='command' if isinstance(message, ff.Command) else 'event',
            context=message.get_context(),
            id_=getattr(message, '_id', str(uuid.uuid4()))
        ))
