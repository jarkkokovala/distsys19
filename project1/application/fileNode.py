from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
import utility.logger


class FileNode:
    logger = utility.logger.get_logger('FileNode')

    def __init__(self, ip_address, port, name_node_ip_address, name_node_port, file_root):
        """
        Initialize the node
        :param ip_address: Ip address
        :param port: Port number
        :param handler_class: Http handler class, should derive from BaseHTTPRequestHandler
        :param name_node_ip_address: ip address of the name node
        :param name_node_port: port of the name node
        :return: void
        """
        self.address = (ip_address, port)
        self.name_node_address = (name_node_ip_address, name_node_port)
        self.file_root = file_root

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
        server = HTTPServer(self.address, FileNodeHTTPRequestHandler)
        FileNode.logger.info('Setting name node address to %s port %i', self.name_node_address[0], self.name_node_address[1])

        FileNode.logger.info('Listening to %s port %i', self.address[0], self.address[1])
        server.serve_forever()

    def register_name_server(self):
        pass


class FileNodeHTTPRequestHandler(BaseHTTPRequestHandler):
    logger = utility.logger.get_logger('FileNodeHTTPRequestHandler')

    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def _message(self, content):
        return content.encode("utf8")  # NOTE: must return a bytes object!

    def do_GET(self):
        self._set_headers()
        self.wfile.write(self._message('This is the file node at %s' % datetime.now().strftime("%m/%d/%Y, %H:%M:%S")))
        # FileNodeHTTPRequestHandler.logger.info()
