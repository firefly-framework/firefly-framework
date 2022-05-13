from __future__ import annotations

from pprint import pprint
from typing import Container, Optional, Type

from devtools import debug
from pydantic import BaseConfig, BaseModel, create_model, Field
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.properties import ColumnProperty, RelationshipProperty


class OrmConfig(BaseConfig):
    orm_mode = True


def pydantic_model_from_entity(db_model: Type, stack: dict = None) -> Type[BaseModel]:
    stack = stack or {}
    if db_model in stack:
        return stack[db_model]
    stack[db_model] = {}
    mapper = inspect(db_model)
    fields = {}
    for attr in mapper.attrs:
        if isinstance(attr, ColumnProperty):
            if attr.columns:
                name = attr.key
                column = attr.columns[0]
                python_type: Optional[type] = None
                if hasattr(column.type, "impl"):
                    if hasattr(column.type.impl, "python_type"):
                        python_type = column.type.impl.python_type
                elif hasattr(column.type, "python_type"):
                    python_type = column.type.python_type
                assert python_type, f"Could not infer python_type for {column}"
                default = None
                if column.default is None and not column.nullable:
                    default = ...
                fields[name] = (python_type, default)

    for k, v in getattr(mapper, '_init_properties').items():
        fields[k] = (pydantic_model_from_entity(v.entity.class_, stack), ...)
        # fields[k] = (v.entity.class_, ...)

    debug(fields)
    pydantic_model = create_model(
        db_model.__name__, __config__=OrmConfig, **fields  # type: ignore
    )
    stack[db_model] = pydantic_model
    return pydantic_model
