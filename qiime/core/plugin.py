from qiime.core.util import is_uri, get_feature_from_uri
from qiime.types import Artifact
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
        self._types = {}

    def register_method(self, name):
        def decorator(function):
            fn_name = function.__name__
            uri = "%s/methods/%s" % (self.uri, fn_name)
            if self.has_method(fn_name):
                raise Exception()

            self._methods[fn_name] = Method(function, uri, name,
                                            function.__doc__,
                                            function.__annotations__)
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
            if self.has_type(cls_name):
                raise Exception()

            uri = "%s/types/%s" % (self.uri, cls_name)
            cls.uri = uri
            self._types[cls_name] = Type(uri, name, cls.__doc__, cls)
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

    def has_type(self, name):
        if is_uri(name, 'types'):
            name = get_feature_from_uri(name, 'types')
        return name in self._types

    def get_type(self, name):
        if is_uri(name, 'types'):
            name = get_feature_from_uri(name, 'types')
        if self.has_type(name):
            return self._types[name]
        else:
            raise Exception()

    def get_types(self):
        return self._types.copy()
