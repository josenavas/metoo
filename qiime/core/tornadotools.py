import re
from collections import defaultdict

from tornado.web import RequestHandler, url

GET = 1
POST = 2
PUT = 4
DELETE = 8

_urls = defaultdict(dict)

_url_param_regex = re.compile(r':[^/]+')

def yield_urls():
    for key, value in _urls.items():
        class APIHandler(RequestHandler):
            def set_default_headers(self):
                self.set_header("Access-Control-Allow-Origin", "*")

            def options(self):
                pass

        for method, action in value.items():
            setattr(APIHandler, method, action)

        yield url(key, APIHandler)

def route(path, method, params=(), authenticate=True):
    path = _to_regex_path(path)

    def decorator(function):
        def wrapped_function(request_handler, *args, **kwargs):
            for param_name in params:
                kwargs[param_name] = request_handler.get_argument(param_name, default=None)
            if authenticate:
                # TODO: Authenticate here
                pass
            # TODO: validate parameters passed
            if request_handler.request.method == 'POST' or request_handler.request.method == 'PUT':
                args = list(args)
                # TODO: get smarter about passing only the needed data instead
                # of a full request object.
                args.insert(0, request_handler.request)
            request_handler.write(function(*args, **kwargs))

        if method == GET:
            _urls[path]['get'] = wrapped_function
        elif method == POST:
            _urls[path]['post'] = wrapped_function
        elif method == PUT:
            _urls[path]['put'] = wrapped_function
        elif method == DELETE:
            _urls[path]['delete'] = wrapped_function

        return function
    return decorator

def _to_regex_path(path):
    return _url_param_regex.sub(r'([^/]+)', path)
