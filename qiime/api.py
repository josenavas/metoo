from qiime.core.registry import plugin_registry
from qiime.core.tornadotools import route, GET, POST, PUT, DELETE, yield_urls
from qiime.db import get_connection

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

@route('/artifacts', POST, params=['name', 'artifact_type'])
def create_artifact(request, name, artifact_type):
    data = get_file_data(request)
    if data is None:
        raise ValueError("Cannot create artifact: missing uploaded file.")

    conn = get_connection()
    c = conn.cursor()

    row = (name, artifact_type, data)
    c.execute("INSERT INTO artifact (name, type, data) VALUES (?, ?, ?)", row)
    artifact_id = c.lastrowid

    c.close()
    conn.commit()
    return {
        'artifact_id': artifact_id
    }

@route('/artifacts/(.+)', GET)
def artifact_info(artifact_id):
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT name, type, data FROM artifact WHERE id = ?",
              (artifact_id,))
    row = c.fetchone()

    # TODO handle the case where the artifact doesn't exist

    c.close()
    conn.commit()

    # TODO fix these names...
    return {
        'artifact_id': artifact_id,
        'name': row[0],
        'artifact_type': row[1],
        'bytes': len(row[2])
    }

@route('/artifacts/(.+)', PUT, params=['name', 'artifact_type'])
def update_artifact(request, artifact_id, name=None, artifact_type=None):
    data = get_file_data(request)

    update_fields = []
    update_values = []

    # TODO we'll need to be smarter about updating type and/or data
    if name is not None:
        update_fields.append('name = ?')
        update_values.append(name)
    if artifact_type is not None:
        update_fields.append('type = ?')
        update_values.append(artifact_type)
    if data is not None:
        update_fields.append('data = ?')
        update_values.append(data)

    conn = get_connection()
    c = conn.cursor()

    query = "UPDATE artifact SET %s WHERE id = ?" % ', '.join(update_fields)
    c.execute(query, update_values + [artifact_id])

    c.close()
    conn.commit()
    return {
        'status': 'success'
    }

@route('/artifacts/(.+)', DELETE)
def delete_artifact(artifact_id):
    conn = get_connection()
    c = conn.cursor()

    # TODO handle the case where the artifact doesn't exist
    c.execute("DELETE FROM artifact WHERE id = ?", (artifact_id,))

    c.close()
    conn.commit()

    return {
        'status': 'success'
    }

def get_file_data(request):
    files = request.files
    if not files:
        return None

    if len(files) > 1:
        raise ValueError("Need 1 named file to upload as artifact, found %d."
                         % len(files))

    upload_name, file_infos = files.popitem()
    if len(file_infos) != 1:
        raise ValueError("Need exactly 1 file to upload as artifact, found "
                         "named file %s with %d payloads." %
                         (repr(upload_name), len(file_infos)))
    file_info = file_infos[0]
    return file_info['body'] # bytes
