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
    Container.configuration = lambda self: ffi.MemoryConfiguration(config)

    c = Container()
    c.registry.set_default_factory(ffi.MemoryRepositoryFactory())

    return c


@pytest.fixture(scope="session")
def kernel(container) -> ff.Kernel:
    return ff.Kernel(container)


@pytest.fixture(scope="session")
def context_map(kernel) -> ff.ContextMap:
    return kernel.context_map


@pytest.fixture(scope="session")
def system_bus(kernel) -> ff.SystemBus:
    return kernel.container.system_bus


@pytest.fixture(scope="session")
def message_factory(kernel) -> ff.MessageFactory:
    return kernel.container.message_factory


@pytest.fixture(scope="function")
def registry(kernel) -> ff.Registry:
    registry = kernel.container.registry
    registry.clear_cache()
    return registry
