def is_uri(self, uri, uri_type):
    return '/' in uri and uri_type in uri

def get_feature_from_uri(uri, feature):
    return uri.split(feature)[-1].split('/')[1]
