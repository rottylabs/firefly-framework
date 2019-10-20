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

from typing import Dict

import firefly.infrastructure as ffi


class DbApiStorageInterfaceRegistry:
    def __init__(self):
        self._connections: Dict[str, ffi.DbApiStorageInterface] = {}

    def add(self, name: str, connection: ffi.DbApiStorageInterface):
        self._connections[name] = connection

    def get(self, name: str) -> ffi.DbApiStorageInterface:
        return self._connections.get(name)

    def disconnect_all(self):
        for name, interface in self._connections.items():
            interface.disconnect()
