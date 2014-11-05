
class PluginRegistry(object):
	def __init__(self):
		self._plugins = {}

	def add(self, plugin):
		self._plugins[plugin.name] = plugin

plugin_registry = PluginRegistry()
