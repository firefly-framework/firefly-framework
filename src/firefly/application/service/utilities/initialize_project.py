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
from pathlib import Path

import firefly.domain as ffd
import inflection


@ffd.cli(
    'firefly generate project',
    alias={'path': ['p'], 'name': ['n']},
    help_='Generate the necessary code to run a Firefly project.',
    args_help={
        'path': 'Where to generate the code',
        'name': 'The name of your project',
    }
)
class InitializeProject(ffd.ApplicationService):
    def __call__(self, name: str = None, path: str = None):
        if name is None:
            name = input('Project name: ')
        snake_case_name = inflection.underscore(name).lower().replace(' ', '_')

        if path is None:
            path = input('Path (.): ')
            if path is None or str(path).strip() == '':
                path = '.'

        original_path = os.getcwd()
        if path != '.':
            os.chdir(path)
        self._generate_files(snake_case_name, name)
        os.chdir(original_path)

    @staticmethod
    def _generate_files(snake_case_name: str, name: str):
        with open('README.md', 'w') as fp:
            fp.write(readme(name))
        with open('setup.py', 'w') as fp:
            fp.write(setup(name))
        with open('firefly.yml', 'w') as fp:
            fp.write(firefly_config(snake_case_name, name))
        with open('pytest.ini', 'w') as fp:
            fp.write(pytest_ini())

        try:
            os.mkdir('src')
            os.mkdir(f'src/{snake_case_name}')
            Path(f'src/{snake_case_name}/__init__.py').touch()
            os.mkdir(f'src/{snake_case_name}/domain')
            Path(f'src/{snake_case_name}/domain/__init__.py').touch()
            os.mkdir(f'src/{snake_case_name}/infrastructure')
            Path(f'src/{snake_case_name}/infrastructure/__init__.py').touch()
            os.mkdir(f'src/{snake_case_name}/application')
            Path(f'src/{snake_case_name}/application/__init__.py').touch()
            os.mkdir(f'src/{snake_case_name}/presentation')
            Path(f'src/{snake_case_name}/presentation/__init__.py').touch()

            os.mkdir('tests')
            os.mkdir('tests/unit')
            os.mkdir('tests/integration')
        except FileExistsError:
            pass

        with open('.env', 'w') as fp:
            fp.write(f"""
CONTEXT={snake_case_name}
""".lstrip())

        with open('.env.local', 'w') as fp:
            fp.write(f"""
DB_DRIVER=sqlite
DB_HOST={snake_case_name}.db
""".lstrip())

        with open('.env-dist', 'w') as fp:
            fp.write(f"""
CONTEXT=
""".lstrip())

        with open('.gitignore', 'w') as fp:
            fp.write(git_ignore())

        os.system('pip freeze > requirements.txt')


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


def firefly_config(snake_case_name: str, name: str):
    return f"""
provider: ~

contexts:
  firefly: ~
  {snake_case_name}: ~

environments:
  local: ~
  dev: ~
  staging: ~
  prod: ~
""".lstrip()


def pytest_ini():
    return """
[pytest]
log_cli = True
log_cli_level = DEBUG
""".lstrip()


def git_ignore():
    return """
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
#  Usually these files are written by a python script from a template
#  before PyInstaller builds the exe, so as to inject date/other infos into it.
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*,cover
.hypothesis/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# pyenv
.python-version

# celery beat schedule file
celerybeat-schedule

# SageMath parsed files
*.sage.py

# dotenv
.env*
!.env*-dist

# virtualenv
.venv
venv/
ENV/
share/
Include/
include/
Scripts/
tcl/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/

# NPM
node_modules/

# Serverless
.serverless/

# PyCharm
.idea/
.idea/**
**.idea/

# VSCode
.vscode/
.vscode/**
**.vscode/

# NPM
node_modules/

# pytest
.pytest_cache/

# Misc
__target__/
requirements-local*
tmp/
""".lstrip()