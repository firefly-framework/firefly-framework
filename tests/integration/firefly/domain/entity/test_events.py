from dataclasses import dataclass

import firefly as ff

import tests.src.todo.domain as todo


def test_inter_context_events(system_bus, registry):
    @dataclass
    class CreateUser(ff.CrudCommand):
        name: str = ff.required()
        email: str = ff.required()

        def __post_init__(self):
            # TODO See if we can reduce some of this configuration.
            self.headers['entity_fqn'] = 'tests.src.iam.domain.entity.User'
            self.headers['operation'] = 'create'
            self.source_context = 'iam'

    system_bus.invoke(CreateUser(name='foo', email='foo@bar.com'))

    todos = registry(todo.TodoList).all()
    assert len(todos) == 1
    assert todos[0].user.name == 'foo'
