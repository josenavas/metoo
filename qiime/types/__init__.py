from abc import ABCMeta, abstractmethod

from qiime.core.util import extract_artifact_id
from qiime.db import ArtifactProxy

class BaseType(object):
    pass

class Artifact(BaseType, metaclass=ABCMeta):
    @property
    @classmethod
    @abstractmethod
    def data_type(cls):
        pass

    @classmethod
    def from_uri(cls, uri):
        artifact_id = extract_artifact_id(uri)
        artifact = ArtifactProxy.get(id=artifact_id)
        data = cls._load_data(artifact.artifact.data)
        return cls(data)

    @classmethod
    @abstractmethod
    def _load_data(cls, data_blob):
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
