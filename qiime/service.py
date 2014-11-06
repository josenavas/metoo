import os
from importlib import import_module

import asyncio
from autobahn.asyncio import wamp, websocket

from qiime.api import get_api_methods
from qiime.core.registry import plugin_registry

def init():
    load_plugins()
    start_server()

def load_plugins():
    import_module('qiime.plugins')

def start_server():
    ## 1) create a WAMP router factory
    router_factory = wamp.RouterFactory()
    ## 2) create a WAMP router session factory
    session_factory = wamp.RouterSessionFactory(router_factory)
    ## 3) Optionally, add embedded WAMP application sessions to the router
    session_factory.add(ProtocolServer())
    ## 4) create a WAMP-over-WebSocket transport server factory
    transport_factory = websocket.WampWebSocketServerFactory(session_factory,
                                                             debug = False,
                                                             debug_wamp = False)
    ## 5) start the server
    loop = asyncio.get_event_loop()
    coro = loop.create_server(transport_factory, '127.0.0.1', 8080)
    server = loop.run_until_complete(coro)
    try:
        ## 6) now enter the asyncio event loop
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.close()

class ProtocolServer(wamp.ApplicationSession):
    def onConnect(self):
        self.join(u"realm1")

    @asyncio.coroutine
    def onJoin(self, details):
        try:
            for api, uri in get_api_methods():
                yield from self.register(api, uri)

            for method in plugin_registry.get_methods():
                yield from self.register(method, method.uri)
        except Exception as e:
            print("could not register procedure: {0}".format(e))
