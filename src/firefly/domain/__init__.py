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

from firefly.domain.value_object import ValueObject
from firefly.domain.entity.entity import Entity, Base as EntityBase
from firefly.domain.entity.aggregate_root import AggregateRoot
from firefly.domain.service.logging.logger import LoggerAware
from firefly.domain.meta.meta_aware import MetaAware
from firefly.domain.repository.search_criteria import SearchCriteria, BinaryOp, EntityAttributeSpy
from firefly.domain.service.serialization.serializer import Serializer
from firefly.domain.service.utils.get_project_root import GetProjectRoot
from firefly.domain.service.http.translate_http_event import TranslateHttpEvent
from firefly.domain.entity.validation.validators import HasLength, HasMaxLength, HasMinLength, NumericValidation, \
    Validation, IsNumeric, IsValidUrl, IsValidEmail, IsInt, IsType, IsFloat, IsOneOf, IsLessThan, IsLessThanOrEqualTo, \
    IsGreaterThanOrEqualTo,IsGreaterThan, IsDatetime, IsMultipleOf, Matches, MatchesPattern
from firefly.domain.service.entity.convert_criteria_to_sqlalchemy import ConvertCriteriaToSqlalchemy
from firefly.domain.entity.messaging.envelope import Envelope
from firefly.domain.service.multithreading.batch_process import BatchProcess
from firefly.domain.factory.cognito_factory import CognitoFactory

from firefly.domain.entity.messaging.message import Message
from firefly.domain.entity.core.endpoints import HttpEndpoint
# from firefly.domain.entity.core.context import Context
from firefly.domain.entity.messaging.event import Event
from firefly.domain.entity.messaging.command import Command
from firefly.domain.entity.messaging.query import Query
from firefly.domain.entity.core.timer import Timer
from firefly.domain.middleware.middleware import Middleware
from firefly.domain.service.annotation.register_middleware import middleware
from firefly.domain.service.messaging.system_bus import SystemBusAware, SystemBus
from firefly.domain.service.logging.logger import Logger, LoggerAware
from firefly.domain.entity.core.configuration import Configuration
from firefly.domain.factory.configuration_factory import ConfigurationFactory
from firefly.domain.service.messaging.message_factory import MessageFactory
from firefly.domain.service.cache.cache import Cache
from firefly.domain.entity.core.mutex import Mutex
from firefly.domain.service.messaging.mutex import RateLimiter
from firefly.domain.service.files.file_system import FileSystem, File
from firefly.domain.value_object import EventBuffer
from firefly.domain.utils import HasMemoryCache, load_class
from firefly.domain.meta.get_arguments import get_arguments
from firefly.domain.service.http.rest_router import RestRouter
from firefly.domain.entity.core.cli import CliApp

from firefly.domain.service.messaging.message_transport import MessageTransport
from firefly.domain.service.core.application_service import ApplicationService

from firefly.domain.event.framework_event import FrameworkEvent

from firefly.domain.repository.connection_factory import ConnectionFactory
from firefly.domain.repository.repository import Repository
from firefly.domain.repository.repository_factory import RepositoryFactory
from firefly.domain.repository.registry import Registry

from firefly.domain.service.core.agent import Agent
from firefly.domain.service.annotation.configuration_annotation import ConfigurationAnnotation
from firefly.domain.service.cache.cache import Cache
from firefly.domain.service.annotation.command_handler import command_handler
from firefly.domain.service.annotation.query_handler import query_handler
from firefly.domain.service.annotation.on import on
from firefly.domain.service.annotation.rest import rest
from firefly.domain.service.annotation.cli import cli
from firefly.domain.service.annotation.timer import timer

from firefly.domain.utils import retry
from firefly.domain.meta.build_argument_list import build_argument_list
from firefly.domain.service.core.application import Application
from firefly.domain.service.resource_name_generator import ResourceNameGenerator

from firefly.domain.service.core.auto_generate_aggregate_apis import AutoGenerateAggregateApis
from firefly.domain.service.crud.create_entity import CreateEntity
from firefly.domain.service.crud.update_entity import UpdateEntity
from firefly.domain.service.crud.delete_entity import DeleteEntity
from firefly.domain.service.crud.query_service import QueryService

from firefly.domain.service.core.handle_invocation import HandleInvocation
from firefly.domain.error import *

from firefly.domain.service.core.fast_api_application import FastApiApplication
from firefly.domain.service.core.chalice_application import ChaliceApplication
from firefly.domain.service.dependency_injection.container import Container
from firefly.domain.service.core.kernel import Kernel

from firefly.domain.hooks.post_boot import PostBoot
