from qiime.types import Artifact
from .method import Method
from .type import Type

class Plugin(object):
    def __init__(self, name, version, author, description):
        self.uri = "org.qiime.plugins.%s" % name
        self.name = name
        self.version = version
        self.author = author
        self.description = description
        self._methods = {}
        self._types = {}

    def register_method(self, name):
        def decorator(function):
            uri = "%s.methods.%s" % (self.uri, function.__name__)
            if self.has_method(uri):
                raise Exception()

            self._methods[uri] = Method(uri, name, function,
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

            uri = "%s.types.%s" % (self.uri, cls.__name__)
            if self.has_type(uri):
                raise Exception()

            self._types[uri] = Type(uri, name, cls.__doc__, 'artifact', cls)
            return cls
        return decorator

    def has_method(self, uri):
        return uri in self._methods

    def get_method(self, uri):
        if self.has_method(uri):
            return self._methods[uri]
        else:
            raise Exception()

    def get_methods(self):
        return self._methods.copy()

    def has_type(self, uri):
        return uri in self._types

    def get_type(self, uri):
        if self.has_type(uri):
            return self._types[uri]
        else:
            raise Exception()

    def get_types(self):
        return self._types.copy()
