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
