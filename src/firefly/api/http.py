from __future__ import annotations

import json

import firefly.domain as ffd
import firefly.application as ffa


@ffd.query_handler()
class DefaultHttpMiddleware(ffd.Middleware):
    def __call__(self, message: ffd.Message, next_: callable):
        try:
            response = next_(message)
            if response.get('origin') != 'http':
                return response
            response = ffd.Response(body=json.dumps(response.body()))
            response.header('status_code', '200')
            response.header('content-type', 'application/json')
        except Exception as e:
            response = ffd.Response()
            response.header('status_code', '500')
            raise e

        return response


@ffd.http(cors=True)
class HttpApi:
    @ffd.http('/services', for_=ffa.GetRegisteredContainerServices)
    def services(self):
        pass
