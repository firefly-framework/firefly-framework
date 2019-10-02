import asyncio
import logging
import sys
from _signal import SIGABRT, SIGILL, SIGINT, SIGSEGV, SIGTERM
from signal import signal
from typing import List, Callable

import websockets
from aiohttp import web


class WebServer:
    def __init__(self, extensions: List[Callable], host: str = '0.0.0.0', port: int = 9000,
                 websocket_host: str = '0.0.0.0', websocket_port: int = 9001):
        self.extensions = extensions
        self.host = host
        self.port = port
        self.websocket_host = websocket_host
        self.websocket_port = websocket_port
        self.app = web.Application()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def add_extension(self, extension: Callable):
        self.extensions.append(extension)

    def run(self):
        self.initialize()

        self.loop.run_until_complete(
            websockets.serve(self._handle_websocket, host=self.websocket_host, port=self.websocket_port)
        )

        print("Server is running", flush=True)
        web.run_app(self.app, host=self.host, port=self.port)

        self._shut_down()

    def initialize(self):
        self._init_logger()

        for extension in self.extensions:
            extension(self)

        for sig in (SIGABRT, SIGILL, SIGINT, SIGSEGV, SIGTERM):
            signal(sig, self._shut_down)()

    async def _handle_websocket(self, websocket, path):
        consumer_task = asyncio.ensure_future(self._consumer(websocket, path))
        producer_task = asyncio.ensure_future(self._producer(websocket, path))
        done, pending = await asyncio.wait([consumer_task, producer_task], return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            task.cancel()

    async def _consumer(self, websocket, path):
        pass

    async def _producer(self, websocket, path):
        pass

    @staticmethod
    def _init_logger():
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)

        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        root.addFilter(ch)

    def _shut_down(self):
        print("Shutting down")
        self.loop.stop()
        self.loop.close()
