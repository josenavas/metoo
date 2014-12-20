import os
from importlib import import_module

from tornado.ioloop import IOLoop
from tornado.web import Application

from framework.api import get_urls
from framework.core.registry import plugin_registry
from framework.db import db, initialize_db

def init():
    load_plugins()
    start_server()

def load_plugins():
    import_module('qiime_plugin')

def start_server():
    app = Application(get_urls())
    app.listen(8888)
    try:
        initialize_db()
        IOLoop.current().start()
    finally:
        print("Closing database connection...")
        db.close()
