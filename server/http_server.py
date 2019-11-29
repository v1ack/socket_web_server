from asyncio import Protocol, transports
from datetime import datetime
from functools import partial
import logging

from aiomisc.service import Service
from aiomisc.io import async_open
from pathlib import Path

try:
    from http_classes import Request, Response, ResponseException
except ImportError:
    from .http_classes import Request, Response, ResponseException

STATIC_PATH = Path(__file__).with_name("static").resolve()

log = logging.getLogger(__name__)


class HTTPProtocol(Protocol):
    transport: transports.BaseTransport
    address: str
    port: int

    def __init__(self, loop, **kwargs):
        super().__init__(**kwargs)
        self.loop = loop

    def connection_made(self, transport: transports.BaseTransport) -> None:
        self.transport = transport
        self.address = transport.get_extra_info("peername")[0]
        self.port = transport.get_extra_info("peername")[1]

        log.debug("Connection made %s:%s", self.address, self.port)

    def connection_lost(self, exc: Exception = None) -> None:
        self.transport.close()

        log.debug("Connection lost %s:%s", self.address, self.port)

    def data_received(self, data: bytes):
        self.loop.create_task(self._handler(data))

    def eof_received(self):
        self.transport.close()

        log.debug("Connection closed %s:%s", self.address, self.port)

    async def _handler(self, data: bytes):
        try:
            request = Request(data.decode())
            response = await self.handler(request)
        except Exception as e:
            log.warning(e)
            response = ResponseException()
            request = None
        log.info(
            "%s -- %s:%s -- %s -- %s", datetime.now(), self.address, self.port, request.path, response.status
        )
        self.transport.write(response())

    @staticmethod
    async def handler(request: Request) -> Response:
        path = STATIC_PATH / request.path
        if path.is_dir():
            path = path / "index.html"
        if path.exists():
            content_type = path.suffix[1:]
            async with async_open(path.resolve(), "rb") as file:
                response = Response(
                    await file.read(), content_type=content_type
                )
        else:
            response = ResponseException(404)
        return response


class HTTPServer(Service):
    server: "asyncio.Server"

    def __init__(self, address: str, port: int, **kwargs):
        self._address = address
        self._port = port
        super().__init__(**kwargs)

    async def start(self):
        self.server = await self.loop.create_server(
            partial(HTTPProtocol, loop=self.loop), self._address, self._port
        )
        log.info("Server is running on %s:%s", self._address, self._port)

    async def stop(self, exception: Exception = None):
        self.server.close()
