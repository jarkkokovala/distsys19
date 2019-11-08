from datetime import datetime
from http.server import BaseHTTPRequestHandler


class FileNode(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def _message(self, content):
        return content.encode("utf8")  # NOTE: must return a bytes object!

    def do_GET(self):
        self._set_headers()
        self.wfile.write(self._message('This is the file node at %s' % datetime.now().strftime("%m/%d/%Y, %H:%M:%S")))

