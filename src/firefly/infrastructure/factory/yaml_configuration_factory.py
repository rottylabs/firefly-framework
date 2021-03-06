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

import importlib
import os
import re
from pprint import pprint

import firefly.domain as ffd
import yaml
from dotenv import load_dotenv
from firefly.domain.entity.core.configuration import Configuration


class YamlConfigurationFactory(ffd.ConfigurationFactory):
    def __call__(self) -> Configuration:
        configuration = Configuration(_config=self._load_config())
        for context, config in configuration.contexts.items():
            module = importlib.import_module(context)
            if module.__file__ is None:
                continue
            try:
                with open(f'{os.path.dirname(module.__file__)}/../../firefly.yml', 'r') as fp:
                    context_config = self._parse(fp.read())
            except FileNotFoundError:
                with open(f'{os.path.dirname(module.__file__)}/../firefly.yml', 'r') as fp:
                    context_config = self._parse(fp.read())

            configuration.contexts[context] = ffd.merge(
                context_config['contexts'].get(context),
                configuration.contexts[context] or {},
            )
        return configuration

    @staticmethod
    def _parse(data: str):
        path_matcher = re.compile(r'.*(\$\{([^}^{]+)\}).*')

        def path_constructor(_, node):
            value = node.value
            match = path_matcher.match(value)
            env_var = match.groups()[1]
            if env_var not in os.environ:
                raise ffd.ConfigurationError(f'Environment variable {env_var} is used in config, but is not set')
            return str(value).replace(f'${{{env_var}}}', os.environ.get(env_var))

        yaml.add_implicit_resolver('!path', path_matcher, None, yaml.SafeLoader)
        yaml.add_constructor('!path', path_constructor, yaml.SafeLoader)

        return yaml.safe_load(data)

    def _load_config(self) -> dict:
        self._load_environment_vars()

        try:
            original_dir = self._move_to_project_root()
        except ffd.ProjectConfigNotFound:
            return {}

        with open('firefly.yml', 'r') as fp:
            config = self._parse(fp.read())
        os.chdir(original_dir)

        return config

    def _load_environment_vars(self):
        env = os.environ.get('ENV', 'local')
        dir_ = self._move_to_project_root()
        for path in ('.env', f'.env.{env}'):
            if os.path.exists(path):
                load_dotenv(dotenv_path=os.path.join(os.getcwd(), path))
        os.chdir(dir_)

    @staticmethod
    def _move_to_project_root() -> str:
        original_dir = os.getcwd()
        # os.chdir(os.environ.get('PWD'))
        while not os.path.exists('firefly.yml'):
            if os.path.realpath(os.getcwd()) == os.path.realpath('..'):
                break
            os.chdir('..')

        if not os.path.exists('firefly.yml'):
            raise ffd.ProjectConfigNotFound()

        return original_dir
