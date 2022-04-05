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

from abc import ABC, abstractmethod
from typing import List, Callable

# from .agent_extension import AgentExtension
# from .application_service import ApplicationService
# from .device import Device
# from .domain_service import DomainService
# from .invoke_on import InvokeOn
# from .kernel import Kernel
# from .query_service import QueryService
from ...entity.core.deployment import Deployment
from ...meta.meta_aware import MetaAware


class Agent(MetaAware, ABC):
    _pre_deployment_hooks: List[Callable] = []
    _post_deployment_hooks: List[Callable] = []

    @abstractmethod
    def __call__(self, deployment: Deployment, **kwargs):
        pass

    def add_pre_deployment_hook(self, cb: Callable):
        self._pre_deployment_hooks.append(cb)

    def add_post_deployment_hook(self, cb: Callable):
        self._post_deployment_hooks.append(cb)
