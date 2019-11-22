import socket
import re
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

sock = socket.socket()

try:
    sock.bind(("", 80))
    log.info("Using port 80")
except OSError:
    sock.bind(("", 8080))
    log.info("Using port 8080")

sock.listen(5)


class Response:
    def __init__(
        self,
        body: str = "",
        content_type: str = "text/html",
        status: int = 200,
    ):
        self.body = body
        self.content_type = content_type
        self.status = status

    def __str__(self):
        return f"""HTTP/1.1 {self.status} OK
Server: SelfMadeServer v0.0.1
Content-type: {self.content_type}
Connection: close

{self.body}
"""

    def __call__(self, *args, **kwargs) -> str:
        return str(self)


class ResponseException(Response):
    def __init__(self, status: int = 500):
        super().__init__(status=status)


class Request:
    HTTP_REQUEST = re.compile(
        r"[A-Z]{3,6}\s[\S]*\sHTTP/[0-9.]*", flags=re.MULTILINE
    )

    def __init__(self, request: str):
        (
            self.method,
            self.address,
            self.http_version,
        ) = self.HTTP_REQUEST.findall(request)[0].split(" ")


while True:
    conn, addr = sock.accept()
    log.info("Connected %r", addr)
    try:
        data = conn.recv(8192)
        request = Request(data.decode())
        log.info(request.address)

        if request.address == "/index.html" or request.address == "/":
            with open("index.html", encoding="utf-8") as file:
                conn.send(Response(file.read())().encode())
        else:
            conn.send(ResponseException(404)().encode())
    except Exception as e:
        log.warning(e)
    finally:
        conn.close()
