import pytest

from test_src.iam.domain.entity import User


def test_query_todos(system_bus, message_factory):
    users = system_bus.query(message_factory.query('iam.Users'))
    assert len(users) == 2


def test_search_criteria_equals(system_bus, message_factory):
    search_criteria = User.c.name == 'foo'
    users = system_bus.query(message_factory.query('iam.Users', {'criteria': search_criteria.to_dict()}))
    assert len(users) == 1


def test_search_criteria_greater_than(system_bus, message_factory):
    search_criteria = User.c.name > 'car'
    users = system_bus.query(message_factory.query('iam.Users', {'criteria': search_criteria.to_dict()}))
    assert len(users) == 1


def test_search_criteria_or(system_bus, message_factory):
    search_criteria = (User.c.name == 'foo') | (User.c.name == 'bar')
    users = system_bus.query(message_factory.query('iam.Users', {'criteria': search_criteria.to_dict()}))
    assert len(users) == 2


@pytest.fixture(autouse=True)
def fixture_data(registry):
    r = registry(User)
    r.add(User(name='foo', email='foo@bar.com'))
    r.add(User(name='bar', email='bar@baz.com'))
