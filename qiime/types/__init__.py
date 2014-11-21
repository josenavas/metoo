from abc import ABCMeta, abstractmethod

class BaseType(object):
    pass

class Artifact(BaseType, metaclass=ABCMeta):
    @property
    @classmethod
    @abstractmethod
    def data_type(cls):
        pass

    @classmethod
    @abstractmethod
    def from_uri(cls, uri):
        pass

    def __init__(self, data):
        self._data = data

    @property
    def data(self):
        return self._data

    #@abstractmethod
    #def upload(self):
    #    pass

    #@abstractmethod
    #def download(self):
    #    pass

    #@abstractmethod
    #def load(self):
    #    pass

    @abstractmethod
    def save(self, study):
        pass
