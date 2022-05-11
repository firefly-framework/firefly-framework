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

from devtools import debug
from mangum import Mangum
from starlette.types import Scope, Receive, Send

import firefly.domain as ffd

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
    __mangum: Mangum = None

    @property
    def _mangum(self) -> Mangum:
        if self.__mangum is None:
            self.__mangum = Mangum(self._kernel.get_application().app, lifespan="off")
        return self.__mangum

    def __call__(self, event, context):
        debug(event)
        return self._mangum(event, context)
