from __future__ import annotations

from abc import ABC

import inflection


class ResourceNameGenerator:
    _project: str = None
    _ff_environment: str = None
    _region: str = None
    _account_id: str = None

    def service_name(self, context: str = ''):
        slug = f'{self._project}_{self._ff_environment}_{context}'.rstrip('_')
        return f'{inflection.camelize(inflection.underscore(slug))}'

    def stream_resource_name(self, context: str):
        return f'{self.service_name(context)}Stream'

    def analytics_application_resource_name(self, context: str):
        return f'{self.service_name(context)}AnalyticsStream'

    def lambda_resource_name(self, name: str, memory: int = None, type_: str = None):
        memory = str(memory or '')
        type_ = str(type_ or '')
        return f'{self.service_name(name)}{memory}Function{type_}'

    def lambda_function_name(self, context: str, type_: str, memory: int = None):
        memory = str(memory or '')
        return f'{self.service_name(context)}{memory}{type_.capitalize()}'

    def queue_name(self, context: str, memory: int = None):
        memory = str(memory or '')
        return f'{self.service_name(context)}{memory}Queue'

    def ddb_resource_name(self, name: str):
        return f'{self.service_name(name)}DdbTable'

    def ddb_table_name(self, context: str):
        return f'{inflection.camelize(context)}-{self._ff_environment}'

    def topic_name(self, context: str):
        return f'{self.service_name(context)}Topic'

    def integration_name(self, context: str = ''):
        return f'{self.service_name(context)}Integration'

    def route_name(self, context: str = ''):
        return f'{self.service_name(context)}Route'

    def stack_name(self, context: str = ''):
        return f'{self.service_name(context)}Stack'

    def subscription_name(self, queue_context: str, topic_context: str = ''):
        slug = f'{self._project}_{self._ff_environment}_{queue_context}_{topic_context}'.rstrip('_')
        return f'{inflection.camelize(inflection.underscore(slug))}Subscription'

    def alarm_subscription_name(self, context: str):
        slug = f'{self._project}_{self._ff_environment}_{context}'
        return f'{inflection.camelize(inflection.underscore(slug))}AlertsSubscription'

    def rest_api_name(self):
        slug = f'{self._project}_{self._ff_environment}'
        return f'{inflection.camelize(inflection.underscore(slug))}Api'

    def rest_api_reference(self):
        return f'{self.rest_api_name()}Id'

    def topic_arn(self, context_name: str):
        return f'arn:aws:sns:{self._region}:{self._account_id}:{self.topic_name(context_name)}'

    def alert_topic_name(self, context: str):
        return f'{self.service_name(context)}FireflyAlerts'

    def alert_topic_arn(self, context: str):
        return f'arn:aws:sns:{self._region}:{self._account_id}:{self.alert_topic_name(context)}'
