from __future__ import annotations

import importlib
import inspect
import sys
from time import sleep

import typing


def retry(cb, valid_cb=None, wait: int = 1, backoff: bool = True, retries: int = 10, catch=Exception):
    while retries > 0:
        try:
            ret = cb()
            if valid_cb is not None and not valid_cb(ret):
                raise RuntimeError('valid_cb is false-y for return value')
            return ret
        except catch as e:
            retries -= 1
            if retries <= 0:
                raise e
            sleep(wait)
            if backoff:
                wait *= 2


def get_arguments(c: callable) -> dict:
    ret = {}
    sig = dict(inspect.signature(c).parameters)

    for k, v in typing.get_type_hints(c).items():
        if k == 'return':
            continue

        ret[k] = {
            'type': v,
            'default': sig[k].default,
            'kind': sig[k].kind,
        }

    return ret


def load_class(fqn: str):
    pieces = fqn.split('.')
    module_name = '.'.join(pieces[0:-1])
    class_ = pieces[-1]

    if module_name not in sys.modules:
        try:
            module = importlib.import_module(module_name)
            return getattr(module, class_)
        except (ImportError, AttributeError):
            return None

    try:
        return getattr(sys.modules[module_name], class_)
    except AttributeError:
        return None
