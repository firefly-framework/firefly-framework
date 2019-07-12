from __future__ import annotations

import json

import firefly.domain as ffd
import firefly.application as ffa


@ffd.query_handler()
class DefaultHttpMiddleware(ffd.Middleware):
    def __call__(self, message: ffd.Message, next_: callable):
        response = next_(message)

        if message.headers.get('origin') == 'http':
            return ffd.HttpMessage(http_headers={'status_code': '200', 'content-type': 'application/json'},
                                   body=json.dumps(response))

        return response


@ffd.http(cors=True)
class HttpApi:
    @ffd.http('/services', target=ffa.GetRegisteredContainerServices)
    def services(self):
        pass
