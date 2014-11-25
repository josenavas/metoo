from abc import ABCMeta, abstractmethod

import qiime.db as db
from qiime.core.util import extract_artifact_id, is_uri, get_feature_from_uri

class BaseType(object, metaclass=ABCMeta):
    name = None
    uri = None

    @classmethod
    @abstractmethod
    def normalize(cls, data):
        pass

    @classmethod
    @abstractmethod
    def load(cls, data):
        pass

    @classmethod
    @abstractmethod
    def annotation(cls):
        pass

class Primitive(BaseType):
    @classmethod
    def annotation(cls):
        return {
            'uri': cls.uri,
            'content': 'primitive'
        }

class Parameterized(BaseType, metaclass=ABCMeta):
    # these properties will be defined by the parameterized type factory

    @property
    @classmethod
    @abstractmethod
    def subtype(cls):
        pass

    @property
    @classmethod
    @abstractmethod
    def args(cls):
        pass

    @classmethod
    def load(cls, data):
        return cls.subtype.load(cls.normalize(data))

    @classmethod
    def annotation(cls):
        return {
            'uri': cls.uri,
            'content': 'parameterized',
            'subtype': cls.subtype,
            'args': cls.args
        }

class Artifact(BaseType, metaclass=ABCMeta):
    @classmethod
    def normalize(cls, uri):
        artifact_id = extract_artifact_id(uri)
        type_uri = db.ArtifactProxy.get(id=artifact_id).artifact.type.uri

        if type_uri != cls.uri:
            raise Exception()

        return uri

    @classmethod
    def annotation(cls):
        return {
            'uri': cls.uri,
            'content': 'artifact'
        }

    @property
    @classmethod
    @abstractmethod
    def data_type(cls):
        pass

    @classmethod
    def load(cls, uri):
        uri = cls.normalize(uri)
        artifact_id = extract_artifact_id(uri)
        artifact = db.ArtifactProxy.get(id=artifact_id)
        return cls.from_blob(artifact.artifact.data)

    @classmethod
    @abstractmethod
    def from_blob(cls, blob):
        pass

    @classmethod
    def save(cls, data, study, name):
        type_ = db.ArtifactType.get(uri=cls.uri)
        artifact = db.Artifact(type=type_, data=cls.to_blob(data), study=study)
        artifact.save()

        artifact_proxy = db.ArtifactProxy(name=name, artifact=artifact,
                                          study=study)
        artifact_proxy.save()

    @classmethod
    @abstractmethod
    def to_blob(cls, data):
        pass

class _TypeRegistry(object):
    def __init__(self):
        self._artifacts = {}
        self._primitives = {}
        self._parameterized = {}

    def primitive(self, cls):
        if not issubclass(cls, BaseType):
            raise TypeError("Class %r must be a subclass of %r." %
                            (cls, BaseType))

        cls_name = cls.__name__
        uri = "/system/types/primitives/%s" % cls_name
        if self.has_type(uri):
            raise Exception()

        cls.uri = uri
        self._primitives[uri] = Type(uri, name, cls.__doc__, cls)
        return cls

    def has_type(self, uri):
        return ((uri in self._artifacts) or
                (uri in self._primitives) or
                (uri in self._parameterized))

    def get_primitive_type(self, name):
        if is_uri(name, 'primitives'):
            name = get_feature_from_uri(name, 'primitives')
        if self.has_primitive_type(name):
            return self._primitives[name]
        else:
            raise Exception()

    def get_primitive_types(self):
        return self._primitives.copy()

    def get_parameterized_types(self):
        return self._parameterized.copy()

type_registry = _TypeRegistry()
