from .method import Method

class Plugin(object):
    def __init__(self, name, version, author, description):
        self.uri = "org.qiime.plugins.%s" % name
        self.name = name
        self.version = version
        self.author = author
        self.description = description
        self._methods = {}

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

    def has_method(self, uri):
        return uri in self._methods

    def get_method(self, uri):
        if self.has_method(uri):
            return self._methods[uri]
        else:
            raise Exception()

    def get_methods(self):
        return self._methods.copy()
