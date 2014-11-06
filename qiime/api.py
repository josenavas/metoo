from qiime.core.registry import plugin_registry

_api_methods = []

def api_method(function):
    _api_methods.append((function, "org.qiime.api.%s" % function.__name__))
    return function

def get_api_methods():
    return _api_methods

@api_method
def list_methods(plugins=None):
    return [m.uri for m in plugin_registry.get_methods(plugins=plugins)]

@api_method
def list_plugins():
    return list(plugin_registry.get_plugin_uris())

@api_method
def method_info(method_uri):
    method = plugin_registry.get_method(method_uri)
    return {
        'uri': method.uri,
        'name': method.name,
        'help': method.docstring,
        # We need to work out the type system before this can be effectively serialized
        # 'annotations': method.annotations
    }
