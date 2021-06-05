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

from firefly.domain import error


class PreDeployHook:
    def __call__(self, for_: str):
        def agent_wrapper(cls):
            try:
                cls.set_agent_extension(for_, 'add_pre_deployment_hook')
            except AttributeError:
                raise error.FrameworkError('@agent used on invalid target')
            return cls

        return agent_wrapper


class PostDeployHook:
    def __call__(self, for_: str):
        def agent_wrapper(cls):
            try:
                cls.set_agent_extension(for_, 'add_post_deployment_hook')
            except AttributeError:
                raise error.FrameworkError('@agent used on invalid target')
            return cls

        return agent_wrapper


class Agent:
    pre_deploy_hook: PreDeployHook = PreDeployHook()
    post_deploy_hook: PostDeployHook = PostDeployHook()

    def __call__(self, name: str):
        def agent_wrapper(cls):
            try:
                cls.set_agent(name)
            except AttributeError:
                raise error.FrameworkError('@agent used on invalid target')
            return cls

        return agent_wrapper


agent = Agent()
