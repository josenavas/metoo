def create_plugin(name, version, author, description):
    from qiime.core.registry import plugin_registry
    from qiime.core.plugin import Plugin

    plugin = Plugin(name, version, author, description)
    plugin_registry.add(plugin)
    return plugin
