from abc import ABCMeta, abstractmethod

import qiime.db as db
from qiime.core.util import extract_artifact_id

class BaseType(object):
    pass

class Artifact(BaseType, metaclass=ABCMeta):
    uri = None

    @property
    @classmethod
    @abstractmethod
    def data_type(cls):
        pass

    @classmethod
    def from_uri(cls, uri):
        artifact_id = extract_artifact_id(uri)
        artifact = db.ArtifactProxy.get(id=artifact_id)
        data = cls.load_data(artifact.artifact.data)
        return cls(data)

    @classmethod
    @abstractmethod
    def load_data(cls, data_blob):
        pass

    def __init__(self, data):
        self._data = data

    @property
    def data(self):
        return self._data

    def save(self, study, name):
        type_ = db.ArtifactType.get(uri=self.uri)
        artifact = db.Artifact(type=type_, data=self.save_data(), study=study)
        artifact.save()

        artifact_proxy = db.ArtifactProxy(name=name, artifact=artifact,
                                          study=study)
        artifact_proxy.save()

    @abstractmethod
    def save_data(self):
        pass
