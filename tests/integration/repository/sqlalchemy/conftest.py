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

import pytest

os.environ['FF_ENVIRONMENT'] = 'local'
os.environ['CONTEXT'] = 'todo'
os.environ['DB_NAME'] = 'firefly'
os.environ['DB_USER'] = 'firefly'
os.environ['DB_PASSWORD'] = 'Abcd1234!'
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_TYPE'] = 'postgresql'
os.environ['DB_PORT'] = '5432'


@pytest.fixture(scope="session")
def config():
    return {
        'contexts': {
            'todo': {
                'entity_module': 'firefly_test.todo.domain',
                'container_module': 'firefly_test.todo.application',
                'application_module': 'firefly_test.todo.application',
                'storage': {
                    'services': {
                        'sqlalchemy': {
                            'connection': {
                                'driver': 'sqlalchemy',
                                'host': 'localhost',
                                'db': 'postgresql',
                            }
                        },
                    },
                    'default': 'sqlalchemy',
                },
            },
            'iam': {
                'entity_module': 'firefly_test.iam.domain',
                'container_module': 'firefly_test.iam.application',
                'application_module': 'firefly_test.iam.application',
                'storage': {
                    'services': {
                        'sqlalchemy': {
                            'connection': {
                                'driver': 'sqlalchemy',
                                'host': 'localhost',
                                'db': 'postgresql',
                            }
                        },
                    },
                    'default': 'sqlalchemy',
                },
            },
            'calendar': {
                'entity_module': 'firefly_test.calendar.domain',
                'storage': {
                    'services': {
                        'sqlalchemy': {
                            'connection': {
                                'driver': 'sqlalchemy',
                                'host': 'localhost',
                                'db': 'postgresql',
                            }
                        },
                    },
                    'default': 'sqlalchemy',
                },
            },
        },
    }
