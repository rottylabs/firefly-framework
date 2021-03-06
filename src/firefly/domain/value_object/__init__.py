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

# __pragma__('skip')
from __future__ import annotations

import typing
from dataclasses import asdict
from typing import List

from firefly.domain.meta.build_argument_list import build_argument_list

from .event_buffer import EventBuffer
from .generic_base import GenericBase
from .parameter import Parameter

from firefly.domain.meta.entity_meta import EntityMeta


class ValueObject(metaclass=EntityMeta):
    _logger = None

    def __init__(self, **kwargs):
        pass

    def to_dict(self):
        # noinspection PyDataclass
        return asdict(self)

    def debug(self, *args, **kwargs):
        return self._logger.debug(*args, **kwargs)

    def info(self, *args, **kwargs):
        return self._logger.info(*args, **kwargs)

    def warning(self, *args, **kwargs):
        return self._logger.warning(*args, **kwargs)

    def error(self, *args, **kwargs):
        return self._logger.error(*args, **kwargs)

    @classmethod
    def from_dict(cls, data: dict, map_: dict = None):
        d = None
        if map_ is not None:
            d = data.copy()
            for source, target in map_.items():
                d[target] = d[source]
        return cls(**build_argument_list(d or data, cls))
    # __pragma__('noskip')
