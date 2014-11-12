from abc import ABCMeta, abstractmethod

class BaseType(object):
    pass

class Artifact(BaseType, metaclass=ABCMeta):
    @property
    @classmethod
    @abstractmethod
    def data_type(cls):
        pass

    @abstractmethod
    def upload(self):
        pass

    @abstractmethod
    def download(self):
        pass

    @abstractmethod
    def load(self):
        pass

    @abstractmethod
    def save(self):
        pass
