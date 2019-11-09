from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
import utility.logger


class NameNode:
    logger = utility.logger.get_logger('NameNode')

    def __init__(self, ip_address, port):
        """
        Initialize the node
        :param ip_address: Ip address
        :param port: Port number
        :return:
        """
        self.address = (ip_address, port)

    def run(self):
        """
        Run the name node
        :return:
        """
        self.run_httpserver()

    def run_httpserver(self):
        """
        Run the HTTPServer
        :return:
        """
        NameNode.logger.info('Listening to %s port %i', self.address[0], self.address[1])
        server = HTTPServer(self.address, NameNodeHTTPRequestHandler)

        server.serve_forever()


class NameNodeHTTPRequestHandler(BaseHTTPRequestHandler):
    logger = utility.logger.get_logger('NameNodeHTTPRequestHandler')

    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def _message(self, content):
        return content.encode("utf8")  # NOTE: must return a bytes object!

    def do_GET(self):
        self._set_headers()
        self.wfile.write(self._message('This is the name node at %s' % datetime.now().strftime("%m/%d/%Y, %H:%M:%S")))

    def do_POST(self):
        self._set_headers()
        self.wfile.write(self._message('This is the name node at %s' % datetime.now().strftime("%m/%d/%Y, %H:%M:%S")))
