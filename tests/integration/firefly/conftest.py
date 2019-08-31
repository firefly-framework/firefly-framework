import firefly as ff
import firefly.infrastructure as ffi
import pytest


@pytest.fixture(scope="session")
def config():
    return {
        'contexts': {
            'todo': {
                'entity_module': 'tests.src.todo.domain.entity',
                'container_module': 'tests.src.todo.application',
                'application_service_module': 'tests.src.todo.application.service',
            },
            'iam': {
                'entity_module': 'tests.src.iam.domain.entity',
                'container_module': 'tests.src.iam.application',
            },
            'calendar': {
                'entity_module': 'tests.src.calendar.domain.entity',
            },
        },
    }


@pytest.fixture(scope="session")
def container(config):
    from firefly.application import Container
    Container.configuration = lambda self: ffi.MemoryConfigurationFactory()(config)

    c = Container()
    c.registry.set_default_factory(ffi.MemoryRepositoryFactory())

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
def registry(container) -> ff.Registry:
    registry = container.registry
    registry.clear_cache()
    return registry
