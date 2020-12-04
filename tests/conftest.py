import logging
import socket

import pytest
from aiohttp import ClientSession
from yarl import URL

from server.__main__ import parser
from server.http_server import HTTPServer

log = logging.getLogger(__name__)


@pytest.fixture
def services(arguments, rest_service):
    return [
        rest_service,
    ]


@pytest.fixture(scope="session")
def localhost():
    params = (
        (socket.AF_INET, "127.0.0.1"),
        (socket.AF_INET6, "::1"),
    )
    for family, addr in params:
        with socket.socket(family, socket.SOCK_STREAM) as sock:
            try:
                sock.bind((addr, 0))
            except Exception:
                pass
            else:
                return addr
    raise RuntimeError("localhost unavailable")


@pytest.fixture
def services(rest_service):
    return [
        rest_service,
    ]


@pytest.fixture
def arguments(localhost, rest_port):
    return parser.parse_args(
        [
            "--log-level=debug",
            f"--api-address={localhost}",
            f"--api-port={rest_port}",
        ]
    )


@pytest.fixture
def rest_port(aiomisc_unused_port_factory) -> int:
    return aiomisc_unused_port_factory()


@pytest.fixture
def rest_url(localhost, rest_port):
    return URL(f"http://{localhost}:{rest_port}")


@pytest.fixture
async def rest_service(arguments):
    return HTTPServer(
        address=arguments.api_address,
        port=arguments.api_port,
    )


async def test_app(rest_url):
    async with ClientSession() as session:
        resp = await session.get(rest_url)
        assert resp.status == 200
