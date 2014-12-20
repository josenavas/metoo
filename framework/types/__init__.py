import types
from abc import ABCMeta, abstractmethod
from importlib import import_module

import framework.db as db
from framework.core.util import extract_artifact_id, is_uri, get_feature_from_uri

class BaseType(object):
    # These are set at registration.
    name = None
    uri = None

    def __init__(self, *args, **kwargs):
        raise Exception("Do not instantiate this.")

    @classmethod
    def dereference(cls, reference):
        """Pass by value dereference producing an instance of the bound type.

        The bound type is the real object expected by a method annotated by
        this class.

        Basic type checking should be performed here via normalize.
        """
        raise NotImplementedError("`dereference` must be implemented by a subclass.")

    @classmethod
    def instantiate(cls, argument, study, name):
        """Instantiate the results of a method on the database.

        Basic type checking should be performed here via check_type.
        """
        raise NotImplementedError("`instantiate` must be implemented by a subclass.")

    @classmethod
    def normalize(cls, reference):
        """Normalize a reference and validate the reference is of correct type.

        """
        raise NotImplementedError("`normalize` must be implemented by a subclass.")


    @classmethod
    def check_type(cls, argument):
        """Check that an instance of the bound type is of the correct type."""
        raise NotImplementedError("`check_type` must be implemented by a subclass.")

    @classmethod
    def annotation(cls):
        raise NotImplementedError("`annotation` must be implemented by a subclass.")

class Primitive(BaseType):
    """Primitives are values that are encoded entirely in the reference itself.

    """
    @classmethod
    def annotation(cls):
        return {
            'uri': cls.uri,
            'content': 'primitive'
        }

    @classmethod
    def check_type(cls, reference):
        cls.normalize(reference)

    @classmethod
    def instantiate(cls, argument, *_):
        # By definition primitives can encode their value in their own
        # reference, so instantiate is actually just a dereference.
        return cls.dereference(argument)

    @classmethod
    def dereference(cls, reference):
        reference = cls.normalize(reference)
        return reference

class Parameterized(BaseType):
    """Parameterized types are produced from type factories.

    They encode some restriction on the type's domain or generalize it to a
    restricted collection.
    """
    # these properties will be defined by the parameterized type factory

    @property
    @classmethod
    def subtype(cls):
        raise NotImplementedError("`subtype` must be set by a subclass.")


    @property
    @classmethod
    def args(cls):
        raise NotImplementedError("`args` must be set by a subclass.")

    @classmethod
    def annotation(cls):
        return {
            'uri': cls.uri,
            'content': 'parameterized',
            'subtype': cls.subtype.annotation(),
            'args': cls.args
        }

class Artifact(BaseType):
    """Basic units of input/output in a study not captured by a primitive.

    """
    @classmethod
    def dereference(cls, reference):
        uri = cls.normalize(reference)
        artifact_id = extract_artifact_id(uri)
        artifact = db.ArtifactProxy.get(id=artifact_id)
        return cls.load(artifact.artifact.data)

    @classmethod
    def instantiate(cls, argument, study, name):
        cls.check_type(argument)
        type_ = db.Type.get(uri=cls.uri)
        artifact = db.Artifact(type=type_, data=cls.save(argument), study=study)
        artifact.save()

        artifact_proxy = db.ArtifactProxy(name=name, artifact=artifact,
                                          study=study)
        artifact_proxy.save()
        return artifact_proxy.uri

    @classmethod
    def normalize(cls, reference):
        if not isinstance(reference, str):
            reference = reference.decode('utf-8')
        artifact_id = extract_artifact_id(reference)
        type_uri = db.ArtifactProxy.get(id=artifact_id).artifact.type.uri

        if type_uri != cls.uri:
            raise TypeError()

        return reference

    @classmethod
    def check_type(cls, argument):
        if not isinstance(argument, cls.data_type):
            raise TypeError("%r is not an instance of %r." % (argument,
                                                              cls.data_type))

    @classmethod
    def annotation(cls):
        return {
            'uri': cls.uri,
            'content': 'artifact'
        }

    @property
    @classmethod
    def data_type(cls):
        """Developer-defined property for describing the bound type."""
        raise NotImplementedError("`data_type` must be set by a subclass.")

    @classmethod
    def load(cls, blob):
        """Load an instance from database.

        """
        raise NotImplementedError("`load` must be implemented by a subclass.")

    @classmethod
    def save(cls, blob):
        """Save an instance to the database.

        """
        raise NotImplementedError("`save` must be implemented by a subclass.")


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

        def wrapped_factory(*args, **kwargs):
            param_type = function(*args, **kwargs)
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
