from dataclasses import dataclass, field


@dataclass
class Test:
    id: str = field()
    _id: str = field(init=False, repr=False)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value


t = Test(id='foo')

print(t)
