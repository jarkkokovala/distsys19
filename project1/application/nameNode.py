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


    def register_fileNode(self, addrport):
        """
        Register a new filenode
        :param address: Address and port of the node as tuple
        :return:
        """
        self.logger.info('Registered fileNode %s port %i', addrport[0], addrport[1])
        self.fileNodes[addrport] = { 
            "last_heartbeat": time.time(),
            "files": []
        }
    
    def have_fileNode(self, addrport):
        """
        Check if a node is registered with us
        :param addrport:  Address and port of the node as tuple
        :return: true if node is registered, false otherwise
        """

        return addrport in self.fileNodes

    def do_heartbeat(self, addrport):
        """
        Process a heartbeat from a fileNode
        :param addrport: Address and port of the node as tuple
        :return:
        """

        self.logger.info('Received heartbeat from %s port %i', addrport[0], addrport[1])
        self.fileNodes[addrport]["last_heartbeat"] = time.time()

    def update_filelist(self, address, files):
        """
        Update the filelist for a fileNode
        :param addrport: Address and port of the node as tuple
        :return:
        """

        self.logger.info('Updating filelist for %s port %i, %i files', address[0], address[1], len(files))
        self.fileNodes[address]["files"] = files

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

        if query.path == "/register": # Register request from filenode
            if "ip_address" in vars and "port" in vars:
                self.server.node.register_fileNode((vars["ip_address"][0], int(vars["port"][0])))
                self._set_headers()
            else:
                self.send_error(400)
                self.end_headers()
        elif query.path == "/heartbeat": # Heartbeat request from filenode
            if "ip_address" in vars and "port" in vars:
                self.server.node.do_heartbeat((vars["ip_address"][0], int(vars["port"][0])))
                self._set_headers()
            else:
                self.send_error(400)
                self.end_headers()            
        else:
            self.send_error(404)
            self.end_headers()

    def do_POST(self):
        query = urlparse(self.path)
        content_len = int(self.headers.get('Content-Length'))
        if content_len > 0:
            body = self.rfile.read(content_len)

        if query.path == "/filelist": # Filelist update from fileNode
            vars = parse_qs(body)

            if b"ip_address" in vars and b"port" in vars:
                fileNode = (vars[b"ip_address"][0].decode('ascii'), int(vars[b"port"][0].decode('ascii')))

                if self.server.node.have_fileNode(fileNode):
                    if b"file_list" in vars:
                        self.server.node.update_filelist(fileNode, vars[b"file_list"])
                    else:
                        self.server.node.update_filelist(fileNode, [])

                    self._set_headers()
                else:
                    self.send_error(400)
                    self.end_headers()
            else:
                self.send_error(400)
                self.end_headers()
