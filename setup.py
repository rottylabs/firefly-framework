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

import setuptools
from setuptools.command.develop import develop
from setuptools.command.install import install

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name='firefly-framework',
    version='0.1.0',
    author="JD Williams",
    author_email="me@jdwilliams.xyz",
    description="A dependency injection framework for python",
    long_description=long_description,
    # long_description_content_type="text/markdown",
    url="https://github.com/firefly19/python-framework",
    entry_points={
        'console_scripts': ['firefly=firefly.presentation.cli:main'],
        'pytest11': ['firefly=firefly.plugins.pytest']
    },
    install_requires=[
        'aiohttp>=3.5.4',
        'aiohttp-cors>=0.7.0',
        'dateparser>=0.7.4',
        'dirsync>=2.2.3',
        'inflection>=0.3.1',
        'Jinja2>=2.11.1',
        # 'kua>=0.2',
        'python-dateutil>=2.8.1',
        'python-dotenv>=0.10.3',
        'pyyaml>=5.1.1',
        'routes>=2.4.1',
        'terminaltables>=3.1.0',
        # 'transcrypt>=3.7.16',
        'websockets>=8.0.2',
        'firefly-dependency-injection>=0.1',
    ],
    extras_require={
        'OpenApi Generation': ['apispec>=3.3.0', 'docstring_parser>=0.7.1'],
        'Frontend Support': ['transcrypt>=3.7.16']
    },
    packages=setuptools.PEP420PackageFinder.find('src'),
    package_dir={'': 'src'},
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ]
    # cmdclass={
    #     'develop': PostDevelopCommand,
    #     'install': PostInstallCommand,
    # }
)
