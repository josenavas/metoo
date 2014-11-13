from collections import defaultdict

from tornado.web import RequestHandler, url

GET = 1
POST = 2
PUT = 4
DELETE = 8

_urls = defaultdict(dict)

def yield_urls():
    for key, value in _urls.items():
        class APIHandler(RequestHandler):
            pass

        for method, action in value.items():
            setattr(APIHandler, method, action)

        yield url(key, APIHandler)

def route(path, method, params=(), authenticate=True):
    def decorator(function):
        def wrapped_function(self, *args, **kwargs):
            for param_name in params:
                kwargs[param_name] = self.get_argument(param_name, default=None)
            if authenticate:
                # TODO: Authenticate here
                pass
            # TODO: validate parameters passed
            if self.request.method == 'POST' or self.request.method == 'PUT':
                args = list(args)
                # TODO: get smarter about passing only the needed data instead
                # of a full request object.
                args.insert(0, self.request)
            self.write(function(*args, **kwargs))

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
