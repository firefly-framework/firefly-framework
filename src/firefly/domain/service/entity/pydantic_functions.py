from __future__ import annotations

import uuid
from typing import Optional, Type, get_type_hints

from devtools import debug
from pydantic import BaseConfig, BaseModel, create_model, Field
from sqlalchemy.orm.properties import ColumnProperty
import inspect


# class OrmConfig(BaseConfig):
#     orm_mode = True
#
#
# def pydantic_model_from_entity(db_model: Type, stack: dict = None) -> Type[BaseModel]:
#     stack = stack or {}
#     if db_model in stack:
#         return stack[db_model]
#     stack[db_model] = {}
#     mapper = inspect(db_model)
#     fields = {}
#     for attr in mapper.attrs:
#         if isinstance(attr, ColumnProperty):
#             if attr.columns:
#                 name = attr.key
#                 column = attr.columns[0]
#                 python_type: Optional[type] = None
#                 if hasattr(column.type, "impl"):
#                     if hasattr(column.type.impl, "python_type"):
#                         python_type = column.type.impl.python_type
#                 elif hasattr(column.type, "python_type"):
#                     python_type = column.type.python_type
#                 assert python_type, f"Could not infer python_type for {column}"
#                 default = None
#                 if column.default is None and not column.nullable:
#                     default = ...
#                 if db_model.id_name() == name:
#                     default = uuid.uuid4()
#                 fields[name] = (python_type, default)
#
#     for k, v in getattr(mapper, '_init_properties').items():
#         default = [] if v.uselist else {}
#         fields[k] = (pydantic_model_from_entity(v.entity.class_, stack), default)
#
#     pydantic_model = create_model(
#         db_model.__name__, __config__=OrmConfig, **fields  # type: ignore
#     )
#     stack[db_model] = pydantic_model
#     return pydantic_model
#
#
# def entity_from_model(model, entity):
#     params = {}
#     if isinstance(model, list):
#         return list(map(lambda x: entity_from_model(x, entity), model))
#
#     if model == {}:
#         return {}
#
#     for key in model.dict().keys():
#         params[key] = getattr(model, key)
#
#     mapper = inspect(entity)
#     for k, v in getattr(mapper, '_init_properties').items():
#         if params[k] is not None:
#             params[k] = entity_from_model(params[k], v.entity.class_)
#             if params[k] == {}:
#                 del params[k]
#
#     return entity(**params)


def _get_field_model(field: Field):
    """
    Returns the BaseModel of this field if it's associated to one.
    """
    if field.sub_fields:
        for f in field.sub_fields:
            if inspect.isclass(f.type_) and issubclass(f.type_, BaseModel):
                return f.type_
    if inspect.isclass(field.type_) and issubclass(field.type_, BaseModel):
        return field.type_


def marshal(data, model: BaseModel):
    """
    Get a dict/list representation of sqlalchemy models suitable for pydantic.
    """
    if data is None:
        return None

    if isinstance(data, (list, tuple)):
        return [marshal(d, model) for d in data]

    if isinstance(data, Base):
        data = data.__dict__

    ret = {}
    for k, field in model.__fields__.items():
        if k not in data or data[k] is None:
            continue

        ret[k] = _marshal_field(data[k], field)

    return ret


def _marshal_field(data, field: Field):
    if isinstance(data, (list, tuple)):
        return [_marshal_field(d, field) for d in data]

    model = _get_field_model(field)
    if model:
        return marshal(data, model)

    return data
