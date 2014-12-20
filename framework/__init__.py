__version__ = "2.0.0-dev"


def create_plugin(name, version, author, description):
    from framework.core.registry import plugin_registry
    from framework.core.plugin import Plugin

    plugin = Plugin(name, version, author, description)
    plugin_registry.add(plugin)
    return plugin
