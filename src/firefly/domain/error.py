from __future__ import annotations


class RepositoryError(Exception):
    pass


class NoResultFound(RepositoryError):
    pass


class MultipleResultsFound(RepositoryError):
    pass


class FrameworkError(Exception):
    pass


class LogicError(FrameworkError):
    pass


class ConfigurationError(FrameworkError):
    pass


class ProjectConfigNotFound(FrameworkError):
    pass


class ProviderNotFound(FrameworkError):
    pass


class InvalidArgument(FrameworkError):
    pass


class MissingArgument(FrameworkError):
    pass


class MissingRouter(FrameworkError):
    pass


class MessageBusError(FrameworkError):
    pass
