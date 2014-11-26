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
