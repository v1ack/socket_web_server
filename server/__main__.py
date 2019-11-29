import argparse
from os import environ

from aiomisc import entrypoint
import configargparse

try:
    from http_server import HTTPServer
except ImportError:
    from .http_server import HTTPServer

parser = configargparse.ArgumentParser(
    allow_abbrev=False,
    auto_env_var_prefix="SERVER_",
    description="Async HTTP server",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    ignore_unknown_config_file_keys=True,
)

parser.add_argument(
    "-s", "--pool-size", type=int, default=4, help="Thread pool size"
)
parser.add_argument(
    "--log-level",
    default="info",
    choices=("debug", "info", "warning", "error", "fatal"),
    help="Logging options"
)
group = parser.add_argument_group("API Options")
group.add_argument("--address", default="127.0.0.1")
group.add_argument("--port", type=int, default=80)

if __name__ == "__main__":
    arguments = parser.parse_args()
    environ.clear()
    services = [
        HTTPServer(address=arguments.address, port=arguments.port)
    ]
    with entrypoint(
            *services,
            log_level=arguments.log_level,
            pool_size=arguments.pool_size) as loop:
        loop.run_forever()
