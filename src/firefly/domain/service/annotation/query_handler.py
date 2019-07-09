from __future__ import annotations

from typing import Union

from .framework_annotation import FrameworkAnnotation


class QueryHandler(FrameworkAnnotation):
    def name(self) -> str:
        return '__ff_query_handler'

    def __call__(self, query: Union[str, type, None] = None):
        return super().__call__(query=query)


query_handler = QueryHandler()
