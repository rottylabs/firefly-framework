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

import inspect
from typing import Callable, Dict, Type, Union

import firefly.domain as ffd

from .middleware import Middleware
from ..core.application_service import ApplicationService
from ...entity.messaging.query import Query


class QueryResolvingMiddleware(Middleware):
    _context_map: ffd.ContextMap = None

    def __init__(self, query_handlers: Dict[ffd.ApplicationService, Type[Query]] = None):
        self._initialized = False
        self._query_handlers = query_handlers or {}

    def _initialize(self):
        for query, handler in self._query_handlers.items():
            if inspect.isclass(handler):
                self._query_handlers[query] = \
                    self._context_map.get_context(handler.get_class_context()).container.build(handler)
        self._initialized = True

    def __call__(self, message: ffd.Message, next_: Callable) -> ffd.Message:
        if not self._initialized:
            self._initialize()

        args = message.to_dict()
        args['_message'] = message
        for service, query_type in self._query_handlers.items():
            if message.is_this(query_type):
                return service(**ffd.build_argument_list(args, service))
        raise ffd.ConfigurationError(f'No query handler registered for {message}')

    def add_query_handler(self, handler: Union[ApplicationService, Type[ApplicationService]],
                          command: Union[Type[Query], str]):
        if inspect.isclass(handler):
            handler = self._context_map.get_context(handler.get_class_context()).container.build(handler)
        self._query_handlers[handler] = command
