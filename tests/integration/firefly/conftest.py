import firefly as ff
import firefly.infrastructure as ffi
import pytest


@pytest.fixture(scope="session")
def config():
    return {
        'contexts': {
            'todo': {
                'entity_module': 'test_src.todo.domain.entity',
                'container_module': 'test_src.todo.application',
                'application_service_module': 'test_src.todo.application.service',
                'storage': {
                    'connections': {
                        'sqlite': {
                            'type': 'db_api',
                            'driver': 'sqlite',
                            'host': ':memory:'
                            # 'host': '/tmp/todo.db'
                        },
                    },
                    'default': 'sqlite',
                },
            },
            'iam': {
                'entity_module': 'test_src.iam.domain.entity',
                'container_module': 'test_src.iam.application',
                'storage': {
                    'connections': {
                        'sqlite': {
                            'type': 'db_api',
                            'driver': 'sqlite',
                            'host': ':memory:'
                            # 'host': '/tmp/iam.db'
                        },
                    },
                    'default': 'sqlite',
                },
            },
            'calendar': {
                'entity_module': 'test_src.calendar.domain.entity',
                'storage': {
                    'connections': {
                        'sqlite': {
                            'type': 'db_api',
                            'driver': 'sqlite',
                            'host': ':memory:'
                            # 'host': '/tmp/calendar.db'
                        },
                    },
                    'default': 'sqlite',
                },
            },
        },
    }


@pytest.fixture(scope="session")
def container(config):
    from firefly.application import Container
    Container.configuration = lambda self: ffi.MemoryConfigurationFactory()(config)

    c = Container()
    # c.registry.set_default_factory(ffi.MemoryRepositoryFactory())

    c.kernel.boot()

    return c


@pytest.fixture(scope="session")
def kernel(container) -> ff.Kernel:
    return container.kernel


@pytest.fixture(scope="session")
def context_map(container) -> ff.ContextMap:
    return container.context_map


@pytest.fixture(scope="session")
def system_bus(container) -> ff.SystemBus:
    return container.system_bus


@pytest.fixture(scope="session")
def message_factory(container) -> ff.MessageFactory:
    return container.message_factory


@pytest.fixture(scope="function")
def registry(container, request) -> ff.Registry:
    registry = container.registry

    def teardown():
        for context in container.context_map.contexts:
            try:
                context.container.db_api_interface_registry.disconnect_all()
            except AttributeError:
                pass
    request.addfinalizer(teardown)
    # registry.clear_cache()
    return registry
