from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
import utility.logger
import time
import pickle
from urllib.parse import urlparse, parse_qs, unquote
import json
import threading
import sys

class NameNode:
    FILENODE_TIMEOUT = 15 # Seconds after we time out a filenode if it hasn't sent a heartbeat

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
        self.fileNodes_lock = threading.Lock()

    def register_fileNode(self, addrport):
        """
        Register a new filenode
        :param address: Address and port of the node as tuple
        :return:
        """
        self.logger.info('Registered fileNode %s port %i', addrport[0], addrport[1])
        with self.fileNodes_lock:
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

        with self.fileNodes_lock:
            ret = addrport in self.fileNodes
            
        return ret

    def do_heartbeat(self, addrport):
        """
        Process a heartbeat from a fileNode
        :param addrport: Address and port of the node as tuple
        :return:
        """

        self.logger.info('Received heartbeat from %s port %i', addrport[0], addrport[1])
        with self.fileNodes_lock:
            self.fileNodes[addrport]["last_heartbeat"] = time.time()

    def update_filelist(self, addrport, files):
        """
        Update the filelist for a fileNode
        :param addrport: Address and port of the node as tuple
        :param files: the new filelist
        :return:
        """

        self.logger.info('Updating filelist for %s port %i, %i files', addrport[0], addrport[1], len(files))
        with self.fileNodes_lock:
            self.fileNodes[addrport]["files"] = files

    def run(self):
        """
        Run the name node
        :return:
        """

        # Run HTTP server in another thread
        http_thread = threading.Thread(target=self.run_httpserver)
        http_thread.daemon = True

        try:
            http_thread.start()
        except KeyboardInterrupt:
            http_thread.shutdown()
            sys.exit(0)
        
        # Run timered task(s) in main thread
        while True:
            # Check for timed out nodes
            with self.fileNodes_lock:
                for node in list(self.fileNodes):
                    if self.fileNodes[node]["last_heartbeat"] < time.time() - self.FILENODE_TIMEOUT:
                        self.logger.info('Timing out fileNode %s port %i', node[0], node[1])
                        del self.fileNodes[node]
            time.sleep(1)

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
            data = json.loads(body.decode('utf-8'))

            if "ip_address" in data and "port" in data:
                fileNode = (data["ip_address"], data["port"])

                if self.server.node.have_fileNode(fileNode):
                    if "file_list" in data:
                        self.server.node.update_filelist(fileNode, data["file_list"])
                    else:
                        self.server.node.update_filelist(fileNode, [])

                    self._set_headers()
                else:
                    self.send_error(400)
                    self.end_headers()
            else:
                self.send_error(400)
                self.end_headers()
            self._set_headers()
