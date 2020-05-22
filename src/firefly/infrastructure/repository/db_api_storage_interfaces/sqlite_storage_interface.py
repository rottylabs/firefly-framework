#  Copyright (c) 2019 JD Williams
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

import sqlite3
from typing import Type, Optional

import firefly.domain as ffd
import inflection

from ..db_api_storage_interface import DbApiStorageInterface


class SqliteStorageInterface(DbApiStorageInterface):
    def __init__(self, serializer: ffd.Serializer, **config):
        self._serializer = serializer
        super().__init__(config)
        self._connection: Optional[sqlite3.Connection] = None
        self._cache = {}

    def _disconnect(self):
        if self._connection is not None:
            self._connection.close()
            self._connection = None
            self._cache = {}
            self._tables_checked = []

    def _add(self, entity: ffd.Entity):
        cursor = self._connection.cursor()
        sql = f"insert into {self._fqtn(entity.__class__)} (id, obj) values (?, ?)"
        cursor.execute(sql, (entity.id_value(), self._serializer.serialize(entity.to_dict())))
        self._connection.commit()
        self._set(entity)

    def _all(self, entity_type: Type[ffd.Entity], criteria: ffd.BinaryOp = None, limit: int = None):
        cursor = self._connection.cursor()
        cursor.execute(f"select * from {self._fqtn(entity_type)}")

        ret = []
        row = cursor.fetchone()
        while row is not None:
            data = self._serializer.deserialize(row['obj'])
            if criteria is not None and not criteria.matches(data):
                row = cursor.fetchone()
                continue
            e = entity_type.from_dict(data)
            oe = self._get(e)
            if oe is not None:
                e = oe
            else:
                self._set(e)
            ret.append(e)
            if limit is not None and len(ret) >= limit:
                break
            row = cursor.fetchone()

        if limit == 1 and len(ret) > 0:
            return ret[0]

        return ret

    def _find(self, uuid: str, entity_type: Type[ffd.Entity]):
        cursor = self._connection.cursor()
        sql = f"select * from {self._fqtn(entity_type)} where id = ?"
        cursor.execute(sql, (uuid,))
        row = cursor.fetchone()
        if row is not None:
            ret = entity_type.from_dict(self._serializer.deserialize(row['obj']))
            oe = self._get(ret)
            if oe is not None:
                ret = oe
            else:
                self._set(ret)
            return ret

    def _remove(self, entity: ffd.Entity):
        cursor = self._connection.cursor()
        sql = f"delete from {self._fqtn(entity.__class__)} where id = ?"
        cursor.execute(sql, (entity.id_value(),))
        self._connection.commit()
        self._remove_from_cache(entity)

    def _update(self, entity: ffd.Entity):
        cursor = self._connection.cursor()
        sql = f"update {self._fqtn(entity.__class__)} set obj = ? where id = ?"
        cursor.execute(sql, (self._serializer.serialize(entity.to_dict()), entity.id_value()))
        self._connection.commit()
        self._set(entity)

    def _ensure_table_created(self, entity: Type[ffd.Entity]):
        cursor = self._connection.cursor()
        sql = f"""
            create table if not exists {self._fqtn(entity)} (
                id text primary key,
                obj text not null
            )
        """
        cursor.execute(sql)

    def _ensure_connected(self):
        if self._connection is not None:
            return

        driver = self._config['driver']
        try:
            host = self._config['host']
        except KeyError:
            raise ffd.ConfigurationError(f'host is required in db_api connection {self.name}')

        if driver == 'sqlite':
            self._connection = sqlite3.connect(host)
            self._connection.row_factory = sqlite3.Row

    @staticmethod
    def _fqtn(entity: Type[ffd.Entity]):
        return inflection.tableize(entity.__name__)

    def _get(self, entity: ffd.Entity):
        if entity.__class__ in self._cache and entity.id_value() in self._cache[entity.__class__]:
            return self._cache[entity.__class__][entity.id_value()]

    def _set(self, entity: ffd.Entity):
        if entity.__class__ not in self._cache:
            self._cache[entity.__class__] = {}
        self._cache[entity.__class__][entity.id_value()] = entity

    def _remove_from_cache(self, entity: ffd.Entity):
        if entity.__class__ in self._cache and entity.id_value() in self._cache[entity.__class__]:
            del self._cache[entity.__class__][entity.id_value()]
