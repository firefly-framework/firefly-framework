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

from firefly.domain.entity.core.cli_app import CliApp
from firefly.domain.service.logging.logger import LoggerAware
from firefly.domain.service.messaging.system_bus import SystemBusAware


class CliAppExecutor(ABC, SystemBusAware, LoggerAware):
    @abstractmethod
    def run(self, app: CliApp):
        pass
