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

import bz2

from mangum import Mangum

import firefly.domain as ffd
from firefly.domain.service.core.chalice_application import ACCESS_CONTROL_HEADERS

COGNITO_TRIGGERS = (
    'PreSignUp_SignUp', 'PreSignUp_AdminCreateUser', 'PostConfirmation_ConfirmSignUp',
    'PostConfirmation_ConfirmForgotPassword', 'PreAuthentication_Authentication', 'PostAuthentication_Authentication',
    'DefineAuthChallenge_Authentication', 'CreateAuthChallenge_Authentication',
    'VerifyAuthChallengeResponse_Authentication', 'TokenGeneration_HostedAuth', 'TokenGeneration_Authentication',
    'TokenGeneration_NewPasswordChallenge', 'TokenGeneration_AuthenticateDevice', 'TokenGeneration_RefreshTokens',
    'UserMigration_Authentication', 'UserMigration_ForgotPassword', 'CustomMessage_SignUp',
    'CustomMessage_AdminCreateUser', 'CustomMessage_ResendCode', 'CustomMessage_ForgotPassword',
    'CustomMessage_UpdateUserAttribute', 'CustomMessage_VerifyUserAttribute', 'CustomMessage_Authentication'
)


class HandleInvocation:
    _kernel: ffd.Kernel = None
    _handle_error: ffd.HandleError = None
    _context: str = None
    __mangum: Mangum = None
    _s3_client = None
    _serializer: ffd.Serializer = None
    _bucket: str = None

    @property
    def _mangum(self) -> Mangum:
        if self.__mangum is None:
            self.__mangum = Mangum(self._kernel.get_application().app, lifespan="off")
        return self.__mangum

    def __call__(self, event, context):
        return self._handle_chalice(event, context)

    def _handle_fastapi(self, event, context):
        return self._mangum(event, context)

    def _handle_chalice(self, event, context):
        try:
            if isinstance(event, dict):
                print(context)
                print(event)

                if 'PAYLOAD_KEY' in event:
                    print('Loading payload')
                    event = self._load_payload(event.get('PAYLOAD_KEY'))
                    print(event)

                if 'Records' in event:
                    return self._handle_sqs(event)

                if '_name' in event and '_type' in event:
                    services = self._kernel.get_command_handlers() if event.get('_type') == 'command' else \
                        self._kernel.get_query_handlers()
                    function_name = f"{self._context}.{event.get('_name')}"
                    if function_name not in services:
                        raise NotImplementedError()

                    return services[function_name](**ffd.build_argument_list(event, services[function_name]))

                try:
                    method = event['requestContext']['http']['method']
                    if method.lower() == 'options':
                        return {
                            'status_code': 200,
                            'headers': ACCESS_CONTROL_HEADERS,
                            'body': None,
                        }
                except KeyError:
                    pass

                if 'triggerSource' in event and event.get('triggerSource') in COGNITO_TRIGGERS:
                    try:
                        return self._kernel.handle_cognito_event(event, context)
                    except AttributeError:
                        raise NotImplementedError()

                event = self._kernel.translate_http_event(event)
                print(event)
            response = self._kernel.get_application().app(event, context)
            print(response)

            return response
        except Exception as e:
            self._handle_error(e, event, context)
            raise

    def _handle_sqs(self, event):
        for e in event.get('Records'):
            try:
                message = self._kernel.serializer.deserialize(e.get('body'))
            except ValueError:
                message = e.get('body')

            if isinstance(message, dict):
                if '_type' in message:
                    message = getattr(self._kernel.message_factory, message['_type'])(
                        f"{message['_context']}.{message['_name']}", message
                    )
                elif 'Message' in message:
                    message = self._kernel.serializer.deserialize(message.get('Message'))

            if isinstance(message, ffd.Command):
                try:
                    handler = self._kernel.get_command_handlers()[str(message)]
                    handler(**ffd.build_argument_list(message.to_dict(), handler))
                except KeyError as ee:
                    raise ffd.ConfigurationError(f'No command handler registered for message: {message}') from ee

            elif isinstance(message, ffd.Event):
                try:
                    for service in self._kernel.get_event_listeners()[str(message)]:
                        service(**ffd.build_argument_list(message.to_dict(), service))
                except KeyError:
                    pass  # Treat a missing event listener as a noop.

    def _load_payload(self, key: str):
        response = self._s3_client.get_object(
            Bucket=self._bucket,
            Key=key
        )
        data = response['Body'].read()
        if key.endswith('bz2'):
            data = bz2.decompress(data)
        return self._serializer.deserialize(data)
