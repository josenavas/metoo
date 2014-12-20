from framework.core.util import is_uri, get_feature_from_uri
from framework.types import type_registry, Artifact
from .method import Method

class Plugin(object):
    def __init__(self, name, version, author, description):
        self.uri = "/system/plugins/%s" % name
        self.name = name
        self.version = version
        self.author = author
        self.description = description
        self._methods = {}
        self._types = set()

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

    def register_type(self, cls):
        uri = "%s/types/%s" % (self.uri, cls.__name__)
        self._types.add(cls)
        return type_registry.artifact(uri, cls)

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

    def get_types(self):
        return list(self._types)
