import os
from importlib import import_module

from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application, url

from qiime.api import get_api_methods
from qiime.core.registry import plugin_registry

def init():
    load_plugins()
    start_server()

def load_plugins():
    import_module('qiime.plugins')

def start_server():
    app = Application(
            get_api_routes() +
            get_arifact_routes()
        )
    app.listen(8888)
    IOLoop.current().start()


def get_api_routes():
    class APIHandler(RequestHandler):
        def get(self, method_name, argument=None):
            method_lookup = get_api_methods()
            try:
                action = method_lookup[method_name]
            except KeyError:
                self.clear()
                self.set_status(404)
                self.write('404 yo')
                return

            kwargs = {}
            for key, value in self.request.arguments.items():
                kwargs[key] = [v.decode("utf-8") for v in value]

            if argument is not None:
                self.write(action(argument, **kwargs))
            else:
                self.write(action(**kwargs))

    return [url(r'/api/(.+)/(.+)', APIHandler), url(r'/api/(.+)', APIHandler)]

def get_artifact_routes():
    class ArtifactHandler(RequestHandler):
        def get(self):
            pass

        def post(self):
            pass

        def delete(self):
            pass

    return [url(r'/artifacts/(.+)', ArtifactHandler)]
