
class PluginRegistry(object):
	def __init__(self):
		self._plugins = {}

	def add(self, plugin):
		self._plugins[plugin.uri] = plugin

	def get_methods(self):
		for plugin in self._plugins.values():
			for method in plugin.get_methods().values():
				yield method

plugin_registry = PluginRegistry()
