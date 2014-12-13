from urllib.parse import urlparse

def is_uri(uri, uri_type):
    return '/' in uri and uri_type in uri

def get_feature_from_uri(uri, feature):
    return uri.split(feature)[-1].split('/')[1]

def extract_artifact_id(artifact_uri):
    return int(urlparse(artifact_uri).path.split('/')[-1])

def is_list(l):
    # TODO: make this not suck.
    return type(l) == list

def listify_duplicate_keys(job_inputs, decode_to_str=False):
    inputs = {}
    for input_ in job_inputs:
        key = input_.key
        value = input_.value.decode('utf-8') if decode_to_str else input_.value

        if key in inputs:
            if is_list(inputs[key]):
                inputs[key].append(value)
            else:
                inputs[key] = [inputs[key], value]
        else:
            inputs[key] = value
    return inputs
