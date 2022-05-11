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

from firefly.infrastructure.service.aws_agent import AwsAgent
from firefly.infrastructure.factory.yaml_configuration_factory import YamlConfigurationFactory
from firefly.infrastructure.factory.memory_configuration_factory import MemoryConfigurationFactory
from firefly.infrastructure.service.logging.default_logger import DefaultLogger
# from firefly.infrastructure.service.messaging.boto_message_transport import BotoMessageTransport
from firefly.infrastructure.service.storage.load_payload import LoadPayload
from firefly.infrastructure.service.storage.prepare_s3_download import PrepareS3Download
from firefly.infrastructure.service.storage.s3_service import S3Service
from firefly.infrastructure.service.storage.store_large_payloads_in_s3 import StoreLargePayloadsInS3
from firefly.infrastructure.service.storage.boto_s3_service import BotoS3Service
from firefly.infrastructure.repository.sqlalchemy.engine_factory import EngineFactory
from firefly.infrastructure.repository.sqlalchemy_repository_factory import SqlalchemyRepositoryFactory
from firefly.infrastructure.repository.sqlalchemy_repository import SqlalchemyRepository
from firefly.infrastructure.repository.sqlalchemy_connection_factory import SqlalchemyConnectionFactory
from firefly.infrastructure.middleware.begin_transaction import BeginTransaction
from firefly.infrastructure.middleware.authorize_request import AuthorizeRequest
from firefly.infrastructure.middleware.handle_envelope import HandleEnvelope
from firefly.infrastructure.service.cli.argparse_executor import ArgparseExecutor
from firefly.infrastructure.repository.migrate_database import MigrateDatabase
from firefly.infrastructure.service.http.routes_rest_router import RoutesRestRouter
from firefly.infrastructure.service.files.s3_file_system import S3FileSystem
from firefly.infrastructure.factory.cognito_factory import DefaultCognitoFactory
from firefly.infrastructure.service.messaging.chalice_message_transport import ChaliceMessageTransport
