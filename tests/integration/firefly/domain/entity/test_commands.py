from datetime import datetime, timedelta

import pytest

from test_src.todo import TodoList, User


def test_auto_generated_api(system_bus, message_factory, todo):
    system_bus.invoke(message_factory.command('todo.AddTask', {
        'todo_list': todo.id,
        'name': 'my task',
        'due_date': datetime.now() + timedelta(days=1)
    }))

    assert len(todo.tasks) == 1
    assert todo.tasks[0].name == 'my task'


def test_nested_api(system_bus, message_factory, todo):
    system_bus.invoke(message_factory.command('todo.AddTask', {
        'todo_list': todo.id,
        'name': 'my task',
        'due_date': datetime.now() + timedelta(days=1)
    }))
    system_bus.invoke(message_factory.command('todo.CompleteTask', {
        'todo_list': todo.id,
        'task_id': todo.tasks[0].id,
    }))

    assert todo.tasks[0].complete is True


@pytest.fixture()
def todo(registry):
    r = registry(TodoList)
    for l in r.all():
        r.remove(l)

    ret = TodoList(user=User(name='foo'))
    r.add(ret)
    return ret
