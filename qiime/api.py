from qiime.core.registry import plugin_registry
from qiime.core.tornadotools import route, GET, POST, PUT, DELETE, yield_urls

def get_urls():
    return list(yield_urls())

@route('/api/list_methods', GET, params=['plugin'])
def list_methods(plugin=None):
    return {'methods': [m.uri for m in plugin_registry.get_methods(plugin=plugin)]}

@route('/api/list_plugins', GET)
def list_plugins():
    return {'plugins': list(plugin_registry.get_plugin_uris())}

@route('/api/method_info/(.+)', GET)
def method_info(method_uri):
    method = plugin_registry.get_method(method_uri)
    return {
        'uri': method.uri,
        'name': method.name,
        'help': method.docstring,
        'annotations': {
            'artifacts': [],  # (parameterized) artifacts (defined in org.qiime.plugins.[plugin-name].artifacts)
            'parameters': {}, # (parameterized) primitives (defined in org.qiime.types.primitives|parameterized)
            'return': []      # (parameterized) artifacts
        }
    }

@route('/artifacts', POST)
def create_artifact(request):
    pass

@route('/artifacts/(.+)', GET)
def artifact_info(artifact_id):
    pass

@route('/artifacts/(.+)', PUT)
def update_artifact(request, artifact_id):
    pass

@route('/artifacts/(.+)', DELETE)
def delete_artifact(artifact_id):
    pass
