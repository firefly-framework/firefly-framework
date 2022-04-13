#  Copyright (c) 2020 JD Williams
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

import os
import shutil
from datetime import datetime
from pprint import pprint
from time import sleep

import firefly.domain as ff
import firefly.infrastructure as ffi
import inflection
import troposphere.kinesis as kinesis
import troposphere.kinesisanalyticsv2 as analytics
import yaml
from botocore.exceptions import ClientError
from firefly.domain.service.core.agent import Agent
from firefly.domain.service.resource_name_generator import ResourceNameGenerator
from firefly.infrastructure.service.storage.s3_service import S3Service
from troposphere import Template, GetAtt, Ref, Parameter, Output, Export, ImportValue, Join
from troposphere.apigatewayv2 import Api, Stage, Deployment, Integration, Route
from troposphere.awslambda import Function, Code, VPCConfig, Environment, Permission, EventSourceMapping
from troposphere.constants import NUMBER
from troposphere.dynamodb import Table, AttributeDefinition, KeySchema, TimeToLiveSpecification
from troposphere.events import Target, Rule
from troposphere.iam import Role, Policy
from troposphere.s3 import Bucket, LifecycleRule, LifecycleConfiguration
from troposphere.sns import Topic, SubscriptionResource
from troposphere.sqs import Queue, QueuePolicy, RedrivePolicy


class AwsAgent(Agent, ResourceNameGenerator, ff.LoggerAware):
    _configuration: ff.Configuration = None
    _kernel: ff.Kernel = None
    _registry: ff.Registry = None
    _s3_client = None
    _s3_service: S3Service = None
    _sns_client = None
    _cloudformation_client = None
    _adaptive_memory = None
    _account_id: str = None
    _context: str = None

    def __call__(self, deployment: dict, **kwargs):
        self._env = deployment['environment']
        try:
            self._bucket = self._configuration.contexts.get('firefly').get('bucket')
        except AttributeError:
            raise ff.FrameworkError('No deployment bucket configured in firefly')

        memory_settings = self._configuration.contexts.get('firefly').get('memory_settings')
        if memory_settings is not None:
            self._adaptive_memory = '1'
            os.environ['ADAPTIVE_MEMORY'] = '1'
        else:
            self._adaptive_memory = None

        self._deployment = deployment
        self._project = self._configuration.all.get('project')
        aws_config = self._configuration.contexts.get('firefly')
        self._aws_config = aws_config
        self._region = aws_config.get('region')
        self._security_group_ids = aws_config.get('vpc', {}).get('security_group_ids')
        self._subnet_ids = aws_config.get('vpc', {}).get('subnet_ids')

        self._template_key = f'cloudformation/templates/{inflection.dasherize(self.service_name())}.json'
        self._create_project_stack()

        lambda_path = inflection.dasherize(self.lambda_resource_name(self._context))
        template_path = inflection.dasherize(self.service_name(self._context))
        self._code_path = f'lambda/code/{lambda_path}'
        self._code_key = f'{self._code_path}/{datetime.now().isoformat()}.zip'
        self._template_key = f'cloudformation/templates/{template_path}.json'
        self._deploy_service()

    def _deploy_service(self):
        if self._aws_config.get('image_uri') is None:
            self._package_and_deploy_code()

        template = Template()
        template.set_version('2010-09-09')

        memory_size = template.add_parameter(Parameter(
            f'{self.lambda_resource_name(self._context)}MemorySize',
            Type=NUMBER,
            Default=self._aws_config.get('memory_sync', '3008')
        ))

        timeout_gateway = template.add_parameter(Parameter(
            f'{self.lambda_resource_name(self._context)}GatewayTimeout',
            Type=NUMBER,
            Default='30'
        ))

        timeout_async = template.add_parameter(Parameter(
            f'{self.lambda_resource_name(self._context)}AsyncTimeout',
            Type=NUMBER,
            Default='900'
        ))

        role_title = f'{self.lambda_resource_name(self._context)}ExecutionRole'
        role = self._add_role(role_title, template)

        params = {
            'FunctionName': f'{self.service_name(self._context)}Sync',
            'Role': GetAtt(role_title, 'Arn'),
            'MemorySize': Ref(memory_size),
            'Timeout': Ref(timeout_gateway),
            'Environment': self._lambda_environment()
        }

        image_uri = self._aws_config.get('image_uri')
        if image_uri is not None:
            params.update({
                'Code': Code(
                    ImageUri=image_uri
                ),
                'PackageType': 'Image',
            })
        else:
            params.update({
                'Code': Code(
                    S3Bucket=self._bucket,
                    S3Key=self._code_key
                ),
                'Runtime': 'python3.9',
                'Handler': 'app.app',
            })

        if self._security_group_ids and self._subnet_ids:
            params['VpcConfig'] = VPCConfig(
                SecurityGroupIds=self._security_group_ids,
                SubnetIds=self._subnet_ids
            )
        api_lambda = template.add_resource(Function(
            f'{self.lambda_resource_name(self._context)}Sync',
            **params
        ))

        route = inflection.dasherize(self._context)
        proxy_route = f'{route}/{{proxy+}}'
        template.add_resource(Permission(
            f'{self.lambda_resource_name(self._context)}SyncPermission',
            Action='lambda:InvokeFunction',
            FunctionName=f'{self.service_name(self._context)}Sync',
            Principal='apigateway.amazonaws.com',
            SourceArn=Join('', [
                'arn:aws:execute-api:',
                self._region,
                ':',
                self._account_id,
                ':',
                ImportValue(self.rest_api_reference()),
                '/*/*/',
                route,
                '*'
            ]),
            DependsOn=api_lambda
        ))

        if self._adaptive_memory:
            value = '3008' if not self._adaptive_memory else '256'
            try:
                value = int(self._aws_config.get('memory_async'))
            except ValueError:
                pass
            memory_size = template.add_parameter(Parameter(
                f'{self.lambda_resource_name(self._context)}MemorySizeAsync',
                Type=NUMBER,
                Default=value
            ))

        params = {
            'FunctionName': self.lambda_function_name(self._context, 'Async'),
            'Role': GetAtt(role_title, 'Arn'),
            'MemorySize': Ref(memory_size),
            'Timeout': Ref(timeout_async),
            'Environment': self._lambda_environment()
        }

        if image_uri is not None:
            params.update({
                'Code': Code(
                    ImageUri=image_uri
                ),
                'PackageType': 'Image',
            })
        else:
            params.update({
                'Code': Code(
                    S3Bucket=self._bucket,
                    S3Key=self._code_key
                ),
                'Runtime': 'python3.9',
                'Handler': 'app.app',
            })

        if self._security_group_ids and self._subnet_ids:
            params['VpcConfig'] = VPCConfig(
                SecurityGroupIds=self._security_group_ids,
                SubnetIds=self._subnet_ids
            )
        async_lambda = template.add_resource(Function(
            self.lambda_resource_name(self._context, type_='Async'),
            **params
        ))

        if self._adaptive_memory:
            self._add_adaptive_memory_functions(template, timeout_async, role_title, async_lambda)
            # self._add_adaptive_memory_streams(template, context, async_lambda, role)

        # Timers
        for config in self._kernel.get_timers():
            # {
            #     'service': self._build_service(cls),
            #     'id': timer.id,
            #     'command': timer.command,
            #     'environment': timer.environment,
            #     'cron': timer.cron,
            # }
            timer_name = config['command']
            _name = config['service'].__class__.__name__
            target = Target(
                f'{self.service_name(self._context)}AsyncTarget',
                Arn=GetAtt(self.lambda_resource_name(self._context, type_='Async'), 'Arn'),
                Id=self.lambda_resource_name(self._context, type_='Async'),
                Input=f'{{"_context": "{self._context}", "_type": "command", "_name": "{_name}"}}'
            )
            rule = template.add_resource(Rule(
                f'{timer_name}TimerRule',
                ScheduleExpression=f'cron({config["cron"]})',
                State='ENABLED',
                Targets=[target]
            ))
            template.add_resource(Permission(
                f'{timer_name}TimerPermission',
                Action='lambda:invokeFunction',
                Principal='events.amazonaws.com',
                FunctionName=Ref(async_lambda),
                SourceArn=GetAtt(rule, 'Arn')
            ))

        integration = template.add_resource(Integration(
            self.integration_name(self._context),
            ApiId=ImportValue(self.rest_api_reference()),
            PayloadFormatVersion='2.0',
            IntegrationType='AWS_PROXY',
            IntegrationUri=Join('', [
                'arn:aws:lambda:',
                self._region,
                ':',
                self._account_id,
                ':function:',
                Ref(api_lambda),
            ]),
        ))

        template.add_resource(Route(
            f'{self.route_name(self._context)}Base',
            ApiId=ImportValue(self.rest_api_reference()),
            RouteKey=f'ANY /{route}',
            AuthorizationType='NONE',
            Target=Join('/', ['integrations', Ref(integration)]),
            DependsOn=integration
        ))

        template.add_resource(Route(
            f'{self.route_name(self._context)}Proxy',
            ApiId=ImportValue(self.rest_api_reference()),
            RouteKey=f'ANY /{proxy_route}',
            AuthorizationType='NONE',
            Target=Join('/', ['integrations', Ref(integration)]),
            DependsOn=integration
        ))

        # Error alarms / subscriptions

        if 'errors' in self._aws_config:
            alerts_topic = template.add_resource(Topic(
                self.alert_topic_name(self._context),
                TopicName=self.alert_topic_name(self._context)
            ))

            if 'email' in self._aws_config.get('errors'):
                for address in self._aws_config.get('errors').get('email').get('recipients').split(','):
                    template.add_resource(SubscriptionResource(
                        self.alarm_subscription_name(self._context),
                        Protocol='email',
                        Endpoint=address,
                        TopicArn=self._alert_topic_arn(),
                        DependsOn=[alerts_topic]
                    ))

        # Queues / Topics

        subscriptions = {}
        for subscription in self._get_subscriptions():
            if subscription['context'] not in subscriptions:
                subscriptions[subscription['context']] = []
            subscriptions[subscription['context']].append(subscription)

        dlq = template.add_resource(Queue(
            f'{self.queue_name(self._context)}Dlq',
            QueueName=f'{self.queue_name(self._context)}Dlq',
            VisibilityTimeout=905,
            ReceiveMessageWaitTimeSeconds=20,
            MessageRetentionPeriod=1209600
        ))
        self._queue_policy(template, dlq, f'{self.queue_name(self._context)}Dlq', subscriptions)

        queue = template.add_resource(Queue(
            self.queue_name(self._context),
            QueueName=self.queue_name(self._context),
            VisibilityTimeout=905,
            ReceiveMessageWaitTimeSeconds=20,
            MessageRetentionPeriod=1209600,
            RedrivePolicy=RedrivePolicy(
                deadLetterTargetArn=GetAtt(dlq, 'Arn'),
                maxReceiveCount=1000
            ),
            DependsOn=dlq
        ))
        self._queue_policy(template, queue, self.queue_name(self._context), subscriptions)

        template.add_resource(EventSourceMapping(
            f'{self.lambda_resource_name(self._context)}AsyncMapping',
            BatchSize=1,
            Enabled=True,
            EventSourceArn=GetAtt(queue, 'Arn'),
            FunctionName=self.lambda_function_name(self._context, 'Async'),
            DependsOn=[queue, async_lambda]
        ))
        topic = template.add_resource(Topic(
            self.topic_name(self._context),
            TopicName=self.topic_name(self._context)
        ))

        for context_name, list_ in subscriptions.items():
            if context_name == self._context and len(list_) > 0:
                template.add_resource(SubscriptionResource(
                    self.subscription_name(context_name),
                    Protocol='sqs',
                    Endpoint=GetAtt(queue, 'Arn'),
                    TopicArn=self.topic_arn(self._context),
                    FilterPolicy={
                        '_name': [x['name'] for x in list_],
                    },
                    RedrivePolicy={
                        'deadLetterTargetArn': GetAtt(dlq, 'Arn'),
                    },
                    DependsOn=[queue, dlq, topic]
                ))
            elif len(list_) > 0:
                if context_name not in self._context_map.contexts:
                    self._find_or_create_topic(context_name)
                template.add_resource(SubscriptionResource(
                    self.subscription_name(self._context, context_name),
                    Protocol='sqs',
                    Endpoint=GetAtt(queue, 'Arn'),
                    TopicArn=self.topic_arn(context_name),
                    FilterPolicy={
                        '_name': [x['name'] for x in list_]
                    },
                    RedrivePolicy={
                        'deadLetterTargetArn': GetAtt(dlq, 'Arn'),
                    },
                    DependsOn=[queue, dlq]
                ))

        # DynamoDB Table

        ddb_table = template.add_resource(Table(
            self.ddb_resource_name(self._context),
            TableName=self.ddb_table_name(self._context),
            AttributeDefinitions=[
                AttributeDefinition(AttributeName='pk', AttributeType='S'),
                AttributeDefinition(AttributeName='sk', AttributeType='S'),
            ],
            BillingMode='PAY_PER_REQUEST',
            KeySchema=[
                KeySchema(AttributeName='pk', KeyType='HASH'),
                KeySchema(AttributeName='sk', KeyType='RANGE'),
            ],
            TimeToLiveSpecification=TimeToLiveSpecification(
                AttributeName='TimeToLive',
                Enabled=True
            )
        ))

        template.add_output(Output(
            "DDBTable",
            Value=Ref(ddb_table),
            Description="Document table"
        ))

        for cb in self._pre_deployment_hooks:
            cb(template=template, env=self._env)

        self.info('Deploying stack')
        self._s3_client.put_object(
            Body=template.to_json(),
            Bucket=self._bucket,
            Key=self._template_key
        )
        url = self._s3_client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': self._bucket,
                'Key': self._template_key
            }
        )

        stack_name = self.stack_name(self._context)
        try:
            self._cloudformation_client.describe_stacks(StackName=stack_name)
            self._update_stack(self.stack_name(self._context), url)
        except ClientError as e:
            if f'Stack with id {stack_name} does not exist' in str(e):
                self._create_stack(self.stack_name(self._context), url)
            else:
                raise e

        for cb in self._post_deployment_hooks:
            cb(template=template, env=self._env)

        self.info('Done')

    def _add_adaptive_memory_streams(self, template, context: ff.Context, lambda_function, role):
        stream_name = self.stream_resource_name(self._context)
        stream = template.add_resource(kinesis.Stream(
            stream_name,
            Name=stream_name,
            ShardCount=1
        ))

        # sql_text = """
        #                 CREATE OR REPLACE STREAM "DESTINATION_STREAM" (
        #                     "rt" TIMESTAMP,
        #                     "message" CHAR(128),
        #                     "up" BIGINT
        #                 );
                        
        #                 CREATE OR REPLACE PUMP "STREAM_PUMP" AS
        #                     INSERT INTO "DESTINATION_STREAM"
        #                         SELECT STREAM
        #                             FLOOR("SOURCE_SQL_STREAM_001".ROWTIME TO HOUR),
        #                             "message",
        #                             MAX(1)
        #                         FROM "SOURCE_SQL_STREAM_001"
        #                         WHERE "event_type" = 'resource-usage'
        #                         GROUP BY FLOOR("SOURCE_SQL_STREAM_001".ROWTIME TO HOUR), "message"
        #                 ;
        #             """

        # """
        #                             CASE WHEN (AVG(memory_usage) + (STDDEV_SAMP(memory_usage) * 2.58)) > (.9 * max_memory) THEN 1 ELSE 0

        #                             AND (
        #                                 (AVG(memory_usage) + (STDDEV_SAMP(memory_usage) * 2.58)) > (.9 * max_memory)
        #                                 OR (AVG(memory_usage) + (STDDEV_SAMP(memory_usage) * 2.58)) < (.8 * COALESCE(prev_memory_tier, 1000000))
        #                             )
        # """

        sql = """
            CREATE OR REPLACE STREAM "DESTINATION_STREAM" (
                "rt" TIMESTAMP,
                "message" VARCHAR(128),
                "up" BIGINT
            );
    
            CREATE OR REPLACE STREAM "METRICS_STREAM" (
                "rt" TIMESTAMP,
                "message" VARCHAR(128),
                "average" DOUBLE,
                "standard_dev" DOUBLE
            );
    
            CREATE OR REPLACE PUMP "METRICS_PUMP" AS
            INSERT INTO "METRICS_STREAM"
                SELECT STREAM
                    FLOOR(s.ROWTIME TO HOUR),
                    "message",
                    AVG("memory_used"),
                    STDDEV_SAMP("memory_used")
                FROM "PwrLabDevIntegrationStream_001" AS s
                GROUP BY FLOOR(s.ROWTIME TO HOUR), "message";
    
    
            CREATE OR REPLACE PUMP "STREAM_PUMP" AS
            INSERT INTO "DESTINATION_STREAM"
                SELECT STREAM
                    m."rt",
                    m."message",
                    MAX(CASE WHEN (m."average" + (m."standard_dev" * 2.58)) > (.9 * s."max_memory") THEN 1 ELSE 0 END)
                FROM "PwrLabDevIntegrationStream_001" AS s
                JOIN "METRICS_STREAM" AS m
                    ON s."message" = m."message" 
                    AND FLOOR(s.ROWTIME TO HOUR) = m."rt"  
                WHERE 
                        ((m."average" + (m."standard_dev" * 2.58)) > (.9 * s."max_memory"))
                        OR ((m."average" + (m."standard_dev" * 2.58)) < (.8 * s."prev_memory_tier"))
                GROUP BY FLOOR(s.ROWTIME TO HOUR), m."rt", m."message", m."average", m."standard_dev", s."max_memory", s."prev_memory_tier";
                            
        """

        analytics_stream = template.add_resource(analytics.Application(
            self.analytics_application_resource_name(self._context),
            ApplicationName=self.analytics_application_resource_name(self._context),
            ApplicationConfiguration=analytics.ApplicationConfiguration(
                ApplicationCodeConfiguration=analytics.ApplicationCodeConfiguration(
                    CodeContent=analytics.CodeContent(
                        TextContent=sql
                    ),
                    CodeContentType="PLAINTEXT"
                ),
                SqlApplicationConfiguration=analytics.SqlApplicationConfiguration(
                    Inputs=[analytics.Input(
                        InputSchema=analytics.InputSchema(
                            RecordColumns=[
                                analytics.RecordColumn(Mapping='event_type', Name='event_type', SqlType='CHAR(64)'),
                                analytics.RecordColumn(Mapping='message', Name='message', SqlType='CHAR(128)'),
                                analytics.RecordColumn(Mapping='memory_used', Name='memory_used', SqlType='NUMERIC'),
                                analytics.RecordColumn(Mapping='run_time', Name='run_time', SqlType='NUMERIC'),
                                analytics.RecordColumn(Mapping='max_memory', Name='max_memory', SqlType='NUMERIC'),
                                analytics.RecordColumn(Mapping='prev_memory_tier', Name='prev_memory_tier', SqlType='NUMERIC'),
                            ],
                            RecordFormat=analytics.RecordFormat(
                                RecordFormatType="JSON"
                            ),
                        ),
                        KinesisStreamsInput=analytics.KinesisStreamsInput(
                            ResourceARN=GetAtt(stream, 'Arn'),
                        ),
                        NamePrefix=stream_name
                    )]
                )
            ),
            RuntimeEnvironment="SQL-1_0",
            ServiceExecutionRole=GetAtt(role, 'Arn'),
            DependsOn=stream
        ))

        template.add_resource(analytics.ApplicationOutput(
            f'{self.analytics_application_resource_name(self._context)}Output',
            ApplicationName=self.analytics_application_resource_name(self._context),
            Output=analytics.Output(
                DestinationSchema=analytics.DestinationSchema(
                    RecordFormatType="JSON"
                ),
                LambdaOutput=analytics.LambdaOutput(
                    ResourceARN=GetAtt(lambda_function, 'Arn')
                )
            ),
            DependsOn=analytics_stream
        ))

    def _add_adaptive_memory_functions(self, template, context: ff.Context, timeout, role_title, async_lambda):
        memory_settings = self._configuration.contexts.get('firefly').get('memory_settings')
        if memory_settings is None:
            raise ff.ConfigurationError('To use adaptive memory, you must provide a list of memory_settings')

        for memory in memory_settings:
            memory_size = template.add_parameter(Parameter(
                f'{self.lambda_resource_name(self._context)}{memory}MemorySize',
                Type=NUMBER,
                Default=str(memory)
            ))

            params = {
                'FunctionName': self.lambda_function_name(self._context, 'Async', memory=memory),
                'Role': GetAtt(role_title, 'Arn'),
                'MemorySize': Ref(memory_size),
                'Timeout': Ref(timeout),
                'Environment': self._lambda_environment(),
                'DependsOn': async_lambda,
            }

            image_uri = self._aws_config.get('image_uri')
            if image_uri is not None:
                params.update({
                    'Code': Code(
                        ImageUri=image_uri
                    ),
                    'PackageType': 'Image',
                })
            else:
                params.update({
                    'Code': Code(
                        S3Bucket=self._bucket,
                        S3Key=self._code_key
                    ),
                    'Runtime': 'python3.9',
                    'Handler': 'app.app',
                })

            if self._security_group_ids and self._subnet_ids:
                params['VpcConfig'] = VPCConfig(
                    SecurityGroupIds=self._security_group_ids,
                    SubnetIds=self._subnet_ids
                )

            adaptive_memory_lambda = template.add_resource(Function(
                self.lambda_resource_name(self._context, memory=memory),
                **params
            ))

            queue = template.add_resource(Queue(
                self.queue_name(self._context, memory=memory),
                QueueName=self.queue_name(self._context, memory=memory),
                VisibilityTimeout=905,
                ReceiveMessageWaitTimeSeconds=20,
                MessageRetentionPeriod=1209600,
                DependsOn=[adaptive_memory_lambda]
            ))
            # self._queue_policy(template, queue, self.queue_name(self._context), subscriptions)

            template.add_resource(EventSourceMapping(
                f'{self.lambda_resource_name(self._context, memory=memory)}AsyncMapping',
                BatchSize=1,
                Enabled=True,
                EventSourceArn=GetAtt(queue, 'Arn'),
                FunctionName=self.lambda_function_name(self._context, 'Async', memory=memory),
                DependsOn=[queue, adaptive_memory_lambda]
            ))

    def _migrate_schema(self, context: ff.Context):
        # TODO Use sqlalchemy/alembic to migrate schemas.
        for entity in context.entities:
            if issubclass(entity, ff.AggregateRoot) and entity is not ff.AggregateRoot:
                try:
                    repository = self._registry(entity)
                    if isinstance(repository, ffi.RdbRepository):
                        repository.migrate_schema()
                except ff.FrameworkError:
                    self.debug('Could not execute ddl for entity %s', entity)

    def _find_or_create_topic(self, context_name: str):
        arn = f'arn:aws:sns:{self._region}:{self._account_id}:{self.topic_name(context_name)}'
        try:
            self._sns_client.get_topic_attributes(TopicArn=arn)
        except ClientError:
            template = Template()
            template.set_version('2010-09-09')
            template.add_resource(Topic(
                self.topic_name(context_name),
                TopicName=self.topic_name(context_name)
            ))
            self.info(f'Creating stack for context "{context_name}"')
            self._create_stack(self.stack_name(context_name), template)

    def _get_subscriptions(self):
        ret = []
        for event_type, services in self._kernel.get_event_listeners().items():
            if isinstance(event_type, str):
                context_name, event_name = event_type.split('.')
            else:
                context_name = event_type.get_class_context()
                event_name = event_type.__name__
            ret.append({
                'name': event_name,
                'context': context_name,
            })

        return ret

    def _package_and_deploy_code(self):
        self.info('Setting up build directory')
        if not os.path.isdir('./build'):
            os.mkdir('./build')
        if os.path.isdir('./build/python-sources'):
            shutil.rmtree('./build/python-sources', ignore_errors=True)
        os.mkdir('./build/python-sources')

        self.info('Installing source files')
        import subprocess
        subprocess.call([
            'pip', 'install',
            '-r', (self._deployment.get('requirements_file') or 'requirements.txt'),
            '-t', './build/python-sources'
        ])

        self.info('Packaging artifact')
        with open('./build/python-sources/app.py', 'w') as fp:
            fp.write("""from __future__ import annotations
            
import firefly as ff
import logging

logging.getLogger()

kernel = ff.Kernel().boot()
kernel.logger.set_level_to_debug()

# app = kernel.get_application().app


def app(event=None, context=None):
    if isinstance(event, dict):
        event = kernel.translate_http_event(event)
    return kernel.get_application().app(event, context)
""")
        os.chdir('./build/python-sources')
        with open('firefly.yml', 'w') as fp:
            fp.write(yaml.dump(self._configuration.all))

        subprocess.call(['find', '.', '-name', '"*.so"', '-exec', 'strip', '{}', ';'])
        subprocess.call(['find', '.', '-name', '"*.so.*"', '-exec', 'strip', '{}', ';'])
        subprocess.call(['find', '.', '-name', '"*.pyc"', '-exec', 'rm', '-Rf', '{}', ';'])
        subprocess.call(['find', '.', '-name', 'tests', '-type', 'd', '-exec', 'rm', '-R', '{}', ';'])
        for package in ('pandas', 'numpy', 'llvmlite'):
            if os.path.isdir(package):
                subprocess.call(['zip', '-r', package, package])
                subprocess.call(['rm', '-Rf', package])

        file_name = self._code_key.split('/')[-1]
        subprocess.call(['zip', '-r', f'../{file_name}', '.'])
        os.chdir('..')

        self.info('Uploading artifact')
        with open(file_name, 'rb') as fp:
            self._s3_client.put_object(
                Body=fp.read(),
                Bucket=self._bucket,
                Key=self._code_key
            )
        os.chdir('..')

        self._clean_up_old_artifacts()

    def _clean_up_old_artifacts(self):
        response = self._s3_client.list_objects(
            Bucket=self._bucket,
            Prefix=self._code_path
        )

        files = []
        for row in response['Contents']:
            files.append((row['Key'], row['LastModified']))
        if len(files) < 3:
            return

        files.sort(key=lambda i: i[1], reverse=True)
        for key, _ in files[2:]:
            self._s3_client.delete_object(Bucket=self._bucket, Key=key)

    def _create_project_stack(self):
        update = True
        try:
            self._cloudformation_client.describe_stacks(StackName=self.stack_name())
        except ClientError as e:
            if 'does not exist' not in str(e):
                raise e
            update = False

        self.info('Creating project stack')
        template = Template()
        template.set_version('2010-09-09')

        memory_size = template.add_parameter(Parameter(
            f'{self.stack_name()}MemorySize',
            Type=NUMBER,
            Default=self._aws_config.get('memory_sync', '3008')
        ))

        timeout_gateway = template.add_parameter(Parameter(
            f'{self.stack_name()}GatewayTimeout',
            Type=NUMBER,
            Default='30'
        ))

        template.add_resource(Bucket(
            inflection.camelize(inflection.underscore(self._bucket)),
            BucketName=self._bucket,
            AccessControl='Private',
            LifecycleConfiguration=LifecycleConfiguration(Rules=[
                LifecycleRule(Prefix='tmp', Status='Enabled', ExpirationInDays=1)
            ])
        ))

        api = template.add_resource(Api(
            self.rest_api_name(),
            Name=f'{inflection.humanize(self._project)} {inflection.humanize(self._env)} API',
            ProtocolType='HTTP'
        ))

        role_title = f'{self.rest_api_name()}Role'
        self._add_role(role_title, template)

        default_lambda = template.add_resource(Function(
            f'{self.rest_api_name()}Function',
            FunctionName=self.rest_api_name(),
            Code=Code(
                ZipFile='\n'.join([
                    'def handler(event, context):',
                    '    return event'
                ])
            ),
            Handler='index.handler',
            Role=GetAtt(role_title, 'Arn'),
            Runtime='python3.7',
            MemorySize=Ref(memory_size),
            Timeout=Ref(timeout_gateway)
        ))

        integration = template.add_resource(Integration(
            self.integration_name(),
            ApiId=Ref(api),
            IntegrationType='AWS_PROXY',
            PayloadFormatVersion='2.0',
            IntegrationUri=Join('', [
                'arn:aws:lambda:',
                self._region,
                ':',
                self._account_id,
                ':function:',
                Ref(default_lambda),
            ]),
            DependsOn=f'{self.rest_api_name()}Function'
        ))

        template.add_resource(Route(
            self.route_name(),
            ApiId=Ref(api),
            RouteKey='$default',
            AuthorizationType='NONE',
            Target=Join('/', ['integrations', Ref(integration)]),
            DependsOn=[integration]
        ))

        # Deprecated
        template.add_resource(Stage(
            f'{self.rest_api_name()}Stage',
            StageName='v2',
            ApiId=Ref(api),
            AutoDeploy=True
        ))

        # Deprecated
        template.add_resource(Deployment(
            f'{self.rest_api_name()}Deployment',
            ApiId=Ref(api),
            StageName='v2',
            DependsOn=[
                f'{self.rest_api_name()}Stage',
                self.route_name(),
                self.integration_name(),
                self.rest_api_name(),
            ]
        ))

        template.add_resource(Stage(
            f'{self.rest_api_name()}Stage1',
            StageName='api',
            ApiId=Ref(api),
            AutoDeploy=True
        ))

        template.add_resource(Deployment(
            f'{self.rest_api_name()}Deployment1',
            ApiId=Ref(api),
            StageName='api',
            DependsOn=[
                f'{self.rest_api_name()}Stage1',
                self.route_name(),
                self.integration_name(),
                self.rest_api_name(),
            ]
        ))

        template.add_output([
            Output(
                self.rest_api_reference(),
                Export=Export(self.rest_api_reference()),
                Value=Ref(api)
            ),
        ])

        self._s3_client.put_object(
            Body=template.to_json(),
            Bucket=self._bucket,
            Key=self._template_key
        )
        url = self._s3_client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': self._bucket,
                'Key': self._template_key
            }
        )

        if update:
            self._update_stack(self.stack_name(), url)
        else:
            self._create_stack(self.stack_name(), url)

    def _add_role(self, role_name: str, template):
        return template.add_resource(Role(
            role_name,
            Path='/',
            Policies=[
                Policy(
                    PolicyName='root',
                    PolicyDocument={
                        'Version': '2012-10-17',
                        'Statement': [
                            {
                                'Action': ['logs:*'],
                                'Resource': 'arn:aws:logs:*:*:*',
                                'Effect': 'Allow',
                            },
                            {
                                'Action': [
                                    'athena:*',
                                    'cloudfront:CreateInvalidation',
                                    'dynamodb:*',
                                    'ec2:*NetworkInterface',
                                    'ec2:DescribeNetworkInterfaces',
                                    'glue:*',
                                    'kinesis:*',
                                    'kinesisanalytics:*',
                                    'lambda:InvokeFunction',
                                    'rds-data:*',
                                    's3:*',
                                    'secretsmanager:GetSecretValue',
                                    'sns:*',
                                    'sqs:*',
                                ] + self._aws_config.get('permissions', []),
                                'Resource': '*',
                                'Effect': 'Allow',
                            }
                        ]
                    }
                )
            ],
            AssumeRolePolicyDocument={
                'Version': '2012-10-17',
                'Statement': [{
                    'Action': ['sts:AssumeRole'],
                    'Effect': 'Allow',
                    'Principal': {
                        'Service': ['lambda.amazonaws.com', 'kinesisanalytics.amazonaws.com']
                    }
                }]
            }
        ))

    def _create_stack(self, stack_name: str, template: str):
        self._cloudformation_client.create_stack(
            StackName=stack_name,
            TemplateURL=template,
            Capabilities=['CAPABILITY_IAM']
        )
        self._wait_for_stack(stack_name)

    def _update_stack(self, stack_name: str, template: str):

        try:
            self._cloudformation_client.update_stack(
                StackName=stack_name,
                TemplateURL=template,
                Capabilities=['CAPABILITY_IAM']
            )
            self._wait_for_stack(stack_name)
        except ClientError as e:
            if 'No updates are to be performed' in str(e):
                return
            raise e

    def _wait_for_stack(self, stack_name: str):
        status = self._cloudformation_client.describe_stacks(StackName=stack_name)['Stacks'][0]
        while status['StackStatus'].endswith('_IN_PROGRESS'):
            self.info('Waiting...')
            sleep(5)
            status = self._cloudformation_client.describe_stacks(StackName=stack_name)['Stacks'][0]

    def _lambda_environment(self):
        env = (self._configuration.contexts.get(self._context) or {}).get('environment')

        defaults = {
            'PROJECT': self._project,
            'FF_ENVIRONMENT': self._env,
            'ACCOUNT_ID': self._account_id,
            'CONTEXT': self._context,
            'REGION': self._region,
            'BUCKET': self._bucket,
            'DDB_TABLE': self.ddb_table_name(self._context),
        }

        if self._adaptive_memory is not None:
            defaults['ADAPTIVE_MEMORY'] = self._adaptive_memory

        if env is not None:
            defaults.update(env)

        if 'SLACK_ERROR_URL' in os.environ:
            defaults['SLACK_ERROR_URL'] = os.environ.get('SLACK_ERROR_URL')

        return Environment(
            'LambdaEnvironment',
            Variables=defaults
        )

    def _queue_policy(self, template: Template, queue, queue_name: str, subscriptions: dict):
        template.add_resource(QueuePolicy(
            f'{queue_name}Policy',
            Queues=[Ref(queue)],
            PolicyDocument={
                'Version': '2008-10-17',
                'Id': f'{queue_name}Policy',
                'Statement': [{
                    'Action': [
                        'sqs:SendMessage',
                    ],
                    'Effect': 'Allow',
                    'Resource': GetAtt(queue, 'Arn'),
                    'Principal': {
                        'AWS': '*',
                    },
                    'Condition': {
                        'ForAnyValue:ArnEquals': {
                            'aws:SourceArn': [
                                self.topic_arn(name) for name in subscriptions.keys()
                            ]
                        }
                    }
                }]
            },
            DependsOn=queue
        ))
