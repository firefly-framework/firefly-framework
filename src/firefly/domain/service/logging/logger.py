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


class Logger(ABC):
    @abstractmethod
    def debug(self, *args, **kwargs):
        pass

    @abstractmethod
    def info(self, *args, **kwargs):
        pass

    @abstractmethod
    def warning(self, *args, **kwargs):
        pass

    @abstractmethod
    def error(self, *args, **kwargs):
        pass

    @abstractmethod
    def exception(self, *args, **kwargs):
        pass

    @abstractmethod
    def set_level_to_fatal(self):
        pass

    @abstractmethod
    def set_level_to_error(self):
        pass

    @abstractmethod
    def set_level_to_warning(self):
        pass

    @abstractmethod
    def set_level_to_info(self):
        pass

    @abstractmethod
    def set_level_to_debug(self):
        pass

    @abstractmethod
    def disable(self):
        pass

    @abstractmethod
    def get_level(self):
        pass

    @abstractmethod
    def set_level(self, level: any):
        pass


class LoggerAware:
    _logger: Logger = None

    def debug(self, *args, **kwargs):
        return self._logger.debug(*args, **kwargs)

    def info(self, *args, **kwargs):
        return self._logger.info(*args, **kwargs)

    def warning(self, *args, **kwargs):
        return self._logger.warning(*args, **kwargs)

    def error(self, *args, **kwargs):
        return self._logger.error(*args, **kwargs)

    def exception(self, *args, **kwargs):
        return self._logger.exception(*args, **kwargs)
