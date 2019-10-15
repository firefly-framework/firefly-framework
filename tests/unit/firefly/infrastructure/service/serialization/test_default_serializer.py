import firefly.domain as ffd
import firefly.infrastructure as ffi
import pytest


class ThisCommand(ffd.Command):
    x: str = ffd.required()
    y: int = ffd.optional(default=0)


def test_serialize_message(sut: ffi.DefaultSerializer):
    command = ThisCommand(x='foo')
    serialized = sut.serialize(command)
    deserialized = sut.deserialize(serialized)

    assert isinstance(deserialized, ThisCommand)
    assert deserialized.x == 'foo'
    assert deserialized.y == 0


@pytest.fixture()
def sut():
    return ffi.DefaultSerializer()
