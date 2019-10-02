from __future__ import annotations

import json
from json import JSONDecodeError

import firefly.application as ffa
import firefly.domain as ffd


@ffd.query_handler()
class DefaultHttpMiddleware(ffd.Middleware):
    def __call__(self, message: ffd.Message, next_: callable):
        response = next_(message)

        if message.headers.get('origin') == 'http':
            try:
                return ffd.HttpMessage(http_headers={'status_code': '200', 'content-type': 'application/json'},
                                       body=json.dumps(response))
            except (JSONDecodeError, TypeError):
                return response

        return response


@ffd.http(cors=True)
class HttpApi:
    @ffd.http('/services', target=ffa.GetRegisteredContainerServices)
    def services(self):
        pass
