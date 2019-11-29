from datetime import datetime
import socket
import re
import logging
from wsgiref.handlers import format_date_time

from pathlib import Path

STATIC_PATH = Path(__file__).with_name("static").resolve()

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

sock = socket.socket()
sock.bind(("", 80))
sock.listen()


class Response:
    STATUS_CODES = {
        200: "OK",
        403: "Forbidden",
        404: "Not found",
        500: "Internal error",
    }

    CONTENT_TYPES = dict(
        html="text/html; charset=UTF-8",
        json="application/json",
        jpg="image/jpeg",
        png="image/png",
        ico="image/x-icon",
        mp3="audio/mpeg",
        svg="image/svg+xml",
        woff="font/woff",
        woff2="font/woff2",
        mp4="video/mpeg",
        ttf="font/ttf",
        jpeg="image/jpeg",
        gif="image/gif",
        zip="application/zip",
        rar="application/x-rar-compressed",
        rtf="application/rtf",
        sh="application/x-sh",
        doc="application/msword",
        xls="application/vnd.ms-excel",
        ppt="application/vnd.ms-powerpoint",
        mid="audio/midi",
        midi="audio/midi",
        wav="audio/x-wav",
        avi="video/x-msvideo",
        bin="application/octet-stream",
        css="text/css",
        csv="text/csv",
        epub="application/epub+zip",
        ics="text/calendar",
        js="application/javascript",
        mkpg="application/vnd.apple.installer+xml",
        pdf="application/pdf",
        tar="application/x-tar",
        xml="application/xml",
    )

    def __init__(
        self, body: bytes = b"", content_type: str = "html", status: int = 200,
    ):
        self.body = body
        self.content_type = self.CONTENT_TYPES[content_type]
        self.status = status

    def _get_html(self):
        if isinstance(self.body, str):
            self.body = self.body.encode()
        return (
            f"""HTTP/1.1 {self.status} {self.STATUS_CODES[self.status]}
Server: SelfMadeServer v0.0.1
Content-type: {self.content_type}
Content-Length: {len(self.body)}
Connection: close
Date: {format_date_time(datetime.now().timestamp())}

""".encode()
            + self.body
        )

    def __call__(self, *args, **kwargs) -> bytes:
        return self._get_html()


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
        address = self.address.split("?")
        self.path = address[0][1:]
        self.query = address[1] if len(address) == 2 else ""


def handler(request):
    log.info(request.address)
    path = Path(STATIC_PATH, request.path)
    if path.is_dir():
        path = Path(path, "index.html")
    if path.exists():
        content_type = path.suffix[1:]
        with path.open("rb") as file:
            response = Response(file.read(), content_type=content_type)()
    else:
        response = ResponseException(404)()
    return response


if __name__ == "__main__":
    while True:
        conn, addr = sock.accept()
        log.info("Connected %r", addr)
        try:
            data = conn.recv(8192)
            if data:
                try:
                    resp = handler(Request(data.decode()))
                    conn.send(resp)
                except Exception as e:
                    conn.send(ResponseException()())
                    log.warning(e)
        finally:
            conn.close()
