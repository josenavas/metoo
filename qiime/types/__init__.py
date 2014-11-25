import types
from abc import ABCMeta, abstractmethod
from importlib import import_module

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
            'subtype': cls.subtype.uri,
            'args': cls.args
        }

class Artifact(BaseType, metaclass=ABCMeta):
    @classmethod
    def normalize(cls, uri):
        uri = uri.decode('utf-8')
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
        type_ = db.Type.get(uri=cls.uri)
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

    def artifact(self, uri, cls):
        if not issubclass(cls, Artifact):
            raise TypeError("Class %r must be a subclass of %r." %
                            (cls, Artifact))

        if self.has_type(uri):
            raise Exception()

        if cls.name is None:
            cls.name = cls.__name__
        cls.uri = uri

        self._artifacts[uri] = cls
        return cls

    def primitive(self, cls):
        if not issubclass(cls, Primitive):
            raise TypeError("Class %r must be a subclass of %r." %
                            (cls, Primitive))

        cls_name = cls.__name__
        uri = '/system/types/primitives/%s' % cls_name
        if self.has_type(uri):
            raise Exception()

        if cls.name is None:
            cls.name = cls_name
        cls.uri = uri

        self._primitives[uri] = cls
        return cls

    def parameterized(self, function):
        if not isinstance(function, types.FunctionType):
            raise TypeError("%r must be a function." % function)

        uri = '/system/types/parameterized/%s' % function.__name__
        name = function.__name__

        def wrapped_factory(*args):
            param_type = function(*args)
            param_type.uri = uri
            param_type.name = name
            return param_type
        
        wrapped_factory.uri = uri
        wrapped_factory.name = name

        if self.has_type(uri):
            raise Exception()
        self._parameterized[uri] = wrapped_factory

        return wrapped_factory

    def has_type(self, uri):
        return ((uri in self._artifacts) or
                (uri in self._primitives) or
                (uri in self._parameterized))

    def get_type(self, uri):
        if uri in self._artifacts:
            return self._artifacts[uri]
        if uri in self._primitives:
            return self._primitives[uri]
        if uri in self._parameterized:
            return self._parameterized[uri]
        else:
            print(self._parameterized)
            raise ValueError("Unrecognized URI %r." % uri)

    def get_types(self):
        master = {}
        master.update(self._artifacts.copy())
        master.update(self._primitives.copy())
        master.update(self._parameterized.copy())
        return master

    def get_artifact_types(self):
        return self._artifacts.copy()

    def get_primitive_types(self):
        return self._primitives.copy()

    def get_parameterized_types(self):
        return self._parameterized.copy()

type_registry = _TypeRegistry()
