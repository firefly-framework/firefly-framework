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

import firefly.domain as ffd
from firefly.infrastructure.service.aws_agent import AwsAgent


@ffd.cli('firefly deploy', alias={'requirements_file': 'r'})
@ffd.command_handler('firefly.Deploy')
class Deploy(ffd.ApplicationService):
    _config: ffd.Configuration = None
    _agent: AwsAgent = None

    def __call__(self, env: str = 'local', requirements_file: str = None, **kwargs):
        provider = self._config.all.get('provider', 'default')
        if env == 'local':
            provider = 'default'

        self._agent({
            'environment': env,
            'provider': provider,
            'project': self._config.all.get('project'),
            'requirements_file': requirements_file,
        }, **kwargs)
