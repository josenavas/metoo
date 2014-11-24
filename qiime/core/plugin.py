from qiime.core.util import is_uri, get_feature_from_uri
from qiime.types import type_registry, Artifact
from .method import Method
from .type import Type

class Plugin(object):
    def __init__(self, name, version, author, description):
        self.uri = "/system/plugins/%s" % name
        self.name = name
        self.version = version
        self.author = author
        self.description = description
        self._methods = {}
        self._types = set() # set of artifact type uris

    def register_method(self, name):
        def decorator(function):
            fn_name = function.__name__
            uri = "%s/methods/%s" % (self.uri, fn_name)
            if self.has_method(fn_name):
                raise Exception()

            self._methods[fn_name] = Method(uri, name, function,
                                            function.__annotations__,
                                            function.__doc__)
            return function
        return decorator

    def register_workflow(self, name):
        pass

    def register_type(self, name):
        def decorator(cls):
            if not issubclass(cls, Artifact):
                raise TypeError("Class %r must be a subclass of %r." %
                                (cls, Artifact))

            cls_name = cls.__name__
            uri = "%s/types/%s" % (self.uri, cls_name)
            if self.has_type(cls_name):
                raise Exception()

            # create the type...
            cls.uri = uri
            type_ = Type(uri, name, cls.__doc__, cls)

            # ...and register it!
            type_registry.register_artifact_type(type_)
            self._types.add(uri)

            return cls
        return decorator

    def has_method(self, name):
        if is_uri(name, 'methods'):
            name = get_feature_from_uri(name, 'methods')
        return name in self._methods

    def get_method(self, name):
        if is_uri(name, 'methods'):
            name = get_feature_from_uri(name, 'methods')
        if self.has_method(name):
            return self._methods[name]
        else:
            raise Exception()

    def get_methods(self):
        return self._methods.copy()

    def has_type(self, uri):
        if not is_uri(uri, 'types'):
            uri = '%s/types/%s' % (self.uri, uri)
        return uri in self._types

    def get_type(self, uri):
        if not is_uri(uri, 'types'):
            uri = '%s/types/%s' % (self.uri, uri)
        if self.has_type(uri):
            return type_registry.get_type(uri)
        else:
            raise Exception()

    def get_types(self):
        return {u: type_registry.get_type(u) for u in self._types}
