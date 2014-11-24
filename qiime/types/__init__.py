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

class _TypeRegistry(object):
    def __init__(self):
        self._artifacts = {}
        self._primitives = {}
        self._parameterized = {}

    def register_artifact_type(self, artifact_type):
        uri = artifact_type.uri

        if self.has_type(uri):
            raise Exception()

        self._artifacts[uri] = artifact_type

    def has_type(self, uri):
        return ((uri in self._artifacts) or
                (uri in self._primitives) or
                (uri in self._parameterized))

    def get_type(self, uri):
        if not self.has_type(uri):
            raise Exception()

        if uri in self._artifacts:
            return self._artifacts[uri]
        if uri in self._primitives:
            return self._primitives[uri]
        if uri in self._parameterized:
            return self._parameterized[uri]

    @property
    def artifacts(self):
        return self._artifacts.keys()

    @property
    def primitives(self):
        return self._primitives.keys()

    @property
    def parameterized(self):
        return self._parameterized.keys()

type_registry = _TypeRegistry()
