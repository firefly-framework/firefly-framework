from abc import ABC


class GenericBase(ABC):
    def _type(self):
        for b in self.__class__.__dict__['__orig_bases__']:
            if len(b.__dict__['__args__']) == 1:
                return b.__dict__['__args__'][0]
