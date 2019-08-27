import tests.src.calendar.domain as calendar
import tests.src.todo.domain as todo


def test_create_on_event(system_bus, registry, message_factory):
    system_bus.invoke(message_factory.command('iam.CreateUser', {
        'name': 'foo',
        'email': 'foo@bar.com',
    }))

    todos = registry(todo.TodoList).all()
    assert len(todos) == 1
    assert todos[0].user.name == 'foo'
    assert todos[0].name == "foo's TODO List"

    calendars = registry(calendar.Calendar).all()
    assert len(calendars) == 1


def test_delete_on_event(system_bus, registry, message_factory):
    system_bus.invoke(message_factory.command('iam.CreateUser', {
        'name': 'foo',
        'email': 'foo@bar.com',
    }))

    todos = registry(todo.TodoList).all()
    assert len(todos) == 1

    system_bus.invoke(message_factory.command('iam.DeleteUser', {
        'id': todos[0].id,
    }))

    assert len(registry(todo.TodoList).all()) == 0
