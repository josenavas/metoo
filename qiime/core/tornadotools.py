import re
from collections import OrderedDict

from tornado.web import RequestHandler, url

GET = 'get'
POST = 'post'
PUT = 'put'
DELETE = 'delete'

_urls = OrderedDict()

_url_param_regex = re.compile(r'\:[^/]+')

def yield_urls():
    for key, value in _urls.items():
        class APIHandler(RequestHandler):
            def set_default_headers(self):
                self.set_header("Access-Control-Allow-Origin", "*")
                self.set_header("Content-Type", "application/json")

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
                kwargs[param_name] = request_handler.get_argument(param_name, default=None) # TODO only default parameters of None are supported
            if authenticate:
                # TODO: Authenticate here
                pass
            # TODO: validate parameters passed
            args = list(args)
            args.insert(0, request_handler)
            response = function(*args, **kwargs)

            # if a response is None, assume the function handled writing of
            # response. if the response isn't None, assume it's a dict (JSON
            # response)
            if response is not None:
                response.update({
                    'resource': request_handler.request.path,
                    'action': method
                })
                request_handler.write(response)

        if path not in _urls:
            _urls[path] = {}
        _urls[path][method] = wrapped_function

        return function
    return decorator

def _to_regex_path(path):
    return _url_param_regex.sub(r'([^/]+)', path)
