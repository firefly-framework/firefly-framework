from __future__ import annotations

import json
from typing import List

import firefly.domain as ffd
import inflection
from firefly.domain.repository.repository import T


class DbApiObjectRepository(ffd.Repository[T]):
    def __init__(self, connection):
        self._entity_type = self._type()
        self._table = inflection.tableize(self._entity_type)
        self._connection = connection

    def all(self) -> List[T]:
        cursor = self._connection.cursor()
        cursor.execute(f"select obj from {self._table}")
        ret = []
        for data in cursor.fetchall():
            ret.append(self._entity_type(**json.loads(data)))

        return ret

    def add(self, entity: T):
        cursor = self._connection.cursor()
        try:
            cursor.execute(
                f"insert into {self._table} (id, obj) values ('%s', '%s')" %
                (entity.id_value(), json.dumps(entity.to_dict()))
            )
            self._connection.commit()
        except:
            self._connection.rollback()

    def remove(self, entity: T):
        pass

    def update(self, entity: T):
        pass

    def find(self, uuid) -> T:
        pass

    def find_all_matching(self, criteria: ffd.BinaryOp) -> List[T]:
        pass

    def find_one_matching(self, criteria: ffd.BinaryOp) -> T:
        pass
