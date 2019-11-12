from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
import utility.logger
import time
from urllib.parse import urlparse, parse_qs


class NameNode:
    def __init__(self, ip_address, port):
        """
        Initialize the node
        :param ip_address: Ip address
        :param port: Port number
        :return:
        """
        self.address = (ip_address, port)
        self.logger = utility.logger.get_logger('NameNode')
        self.fileNodes = {}


    def register_fileNode(self, address):
        self.logger.info('Registered fileNode %s port %i', address[0], address[1])
        self.fileNodes[address] = { 
            "last_heartbeat": time.time(),
            "files": []
        }
    
    def do_heartbeat(self, address):
        self.logger.info('Received heartbeat from %s port %i', address[0], address[1])
        self.fileNodes[address]["last_heartbeat"] = time.time()

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
        self.logger.info('Listening to %s port %i', self.address[0], self.address[1])
        server = HTTPServer(self.address, NameNodeHTTPRequestHandler)
        server.node = self
        server.logger = self.logger
        server.serve_forever()


class NameNodeHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def _message(self, content):
        return content.encode("utf8")  # NOTE: must return a bytes object!

    def do_GET(self):
        query = urlparse(self.path)
        vars = parse_qs(query.query)

        if query.path == "/register":
            if vars["ip_address"][0] and vars["port"][0]:
                self.server.node.register_fileNode((vars["ip_address"][0], int(vars["port"][0])))
                self.send_response(200)
                self.end_headers()
            else:
                self.send_error(400)
                self.end_headers()
        elif query.path == "/heartbeat":
            if vars["ip_address"][0] and vars["port"][0]:
                self.server.node.do_heartbeat((vars["ip_address"][0], int(vars["port"][0])))
                self.send_response(200)
                self.end_headers()
            else:
                self.send_error(400)
                self.end_headers()            
        else:
            self.send_error(404)
            self.end_headers()

    def do_POST(self):
        self._set_headers()
        self.wfile.write(self._message('This is the name node at %s' % datetime.now().strftime("%m/%d/%Y, %H:%M:%S")))
