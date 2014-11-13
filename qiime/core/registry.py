
class PluginRegistry(object):
    def __init__(self):
        self._plugins = {}

    def add(self, plugin):
        self._plugins[plugin.uri] = plugin

    def get_plugin_uris(self):
        for plugin in self._plugins.values():
            yield plugin.uri

    def get_methods(self, plugin=None):
        if plugin is None:
            plugins = self._plugins.keys()
        else:
            plugins = [plugin]
        for uri in plugins:
            for method in self.get_plugin(uri).get_methods().values():
                yield method

    def get_method(self, uri):
        return self.get_plugin('.'.join(uri.split('.')[:-2])).get_method(uri)

    def get_plugin(self, uri):
        return self._plugins[uri]

plugin_registry = PluginRegistry()
