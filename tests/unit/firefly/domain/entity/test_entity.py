from dataclasses import dataclass
from datetime import datetime, date

import firefly.domain as ffd
import pytest
from firefly.domain.entity.entity import Entity


def test_constructor(sut):
    with pytest.raises(TypeError, match="missing 1 required argument"):
        sut()

    sut(required_field='foo')


def test_default_values(sut):
    s = sut(required_field='foo')
    assert isinstance(s.now, datetime)
    assert isinstance(s.today, date)
    assert s.strings == []


@pytest.fixture()
def sut():
    @dataclass()
    class ConcreteEntity(Entity):
        id: str = ffd.pk()
        strings: str = ffd.list_()
        now: datetime = ffd.now()
        today: date = ffd.today()
        required_field: str = ffd.required()

    return ConcreteEntity
