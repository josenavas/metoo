from framework.core.util import is_uri, get_feature_from_uri

class _PluginRegistry(object):
    def __init__(self):
        self._plugins = {}

    def add(self, plugin):
        self._plugins[plugin.name] = plugin

    def get_plugin_uris(self):
        for plugin in self._plugins.values():
            yield plugin.uri

    def get_plugin(self, name):
        if is_uri(name, 'plugins'):
            name = get_feature_from_uri(name, 'plugins')
        return self._plugins[name]

    def get_methods(self, plugin_name=None):
        if plugin_name is None:
            plugin_names = self._plugins.keys()
        else:
            plugin_names = [plugin_name]
        for name in plugin_names:
            for method in self.get_plugin(name).get_methods().values():
                yield method

    def get_types(self, plugin_name=None):
        if plugin_name is None:
            plugin_names = self._plugins.keys()
        else:
            plugin_names = [plugin_name]
        for name in plugin_names:
            for type_ in self.get_plugin(name).get_types():
                yield type_

plugin_registry = _PluginRegistry()
