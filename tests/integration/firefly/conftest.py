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
            },
            'iam': {
                'entity_module': 'tests.src.iam.domain.entity',
                'container_module': 'tests.src.iam.application',
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
def registry(kernel) -> ff.Registry:
    return kernel.container.registry
