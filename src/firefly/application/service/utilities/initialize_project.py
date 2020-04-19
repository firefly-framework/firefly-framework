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
import os

import firefly.domain as ffd


@ffd.cli('firefly generate project', alias={'path': ['-p'], 'name': ['-n']})
class InitializeProject(ffd.ApplicationService):
    def __call__(self, name: str = None, path: str = None):
        if name is None:
            name = input('Project name: ')

        if path is None:
            path = input('Path (.): ')
            if path is None or str(path).strip() == '':
                path = '.'

        os.chdir(path)
        self._generate_files(name)

    @staticmethod
    def _generate_files(name: str):
        with open('./README.md', 'w') as fp:
            fp.write(readme(name))
        with open('./setup.py', 'w') as fp:
            fp.write(setup(name))
        with open('./firefly.yml', 'w') as fp:
            fp.write(firefly_config(name))
        with open('./pytest.ini', 'w') as fp:
            fp.write(pytest_ini())

        try:
            os.mkdir('src')
            os.mkdir(f'src/{name}')
            os.mkdir(f'src/{name}/domain')
            os.mkdir(f'src/{name}/infrastructure')
            os.mkdir(f'src/{name}/application')
            os.mkdir(f'src/{name}/presentation')
        except FileExistsError:
            pass


def setup(name: str):
    return f"""
import setuptools
from setuptools.command.develop import develop
from setuptools.command.install import install

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name='{name}',
    version='0.1',
    author="",
    author_email="",
    description="Put project description here.",
    long_description=long_description,
    url="",
    entry_points={{
        'console_scripts': ['firefly=firefly.presentation.cli:main']
    }},
    install_requires=[
        'firefly-dependency-injection>=0.1',
    ],
    packages=setuptools.PEP420PackageFinder.find('src'),
    package_dir={{'': 'src'}},
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ]
)
""".lstrip()


def readme(name: str):
    return f"""
{name} README
""".lstrip()


def firefly_config(name):
    return f"""
contexts:
  firefly: ~
  {name}: ~
""".lstrip()


def pytest_ini():
    return """
[pytest]
log_cli = True
log_cli_level = DEBUG
""".lstrip()
