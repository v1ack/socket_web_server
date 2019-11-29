import logging
from datetime import datetime
import re
from pathlib import Path
from wsgiref.handlers import format_date_time

log = logging.getLogger(__name__)


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
Cache-Control: max-age=8600
Connection: keep-alive
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
        self.path = Path(address[0][1:])
        self.query = address[1] if len(address) == 2 else ""

    def __repr__(self):
        return f"<Request {self.method} {self.address}>"
