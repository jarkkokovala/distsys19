import os
import socket
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import sys
import threading
import time
import utility.logger


class FileNode:
    HEARTBEAT_INTERVAL = 5 # seconds

    def __init__(self, ip_address, port, name_node_ip_address, name_node_port, file_system_root):
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
        self.file_system_root = file_system_root
        self.logger = utility.logger.get_logger('FileNode %s:%i' % self.address)
        if not os.path.exists(self.file_system_root):
            os.makedirs(self.file_system_root)

    def run(self):
        """
        Run the name node
        :return:
        """

        # Check that the port is not in use
        self.try_port()

        # Register
        self.register()

        # Run HTTPServer in it's own thread
        http_thread = threading.Thread(target=self.run_httpserver)
        http_thread.daemon = True
        try:
            http_thread.start()
        except KeyboardInterrupt:
            http_thread.shutdown()
            sys.exit(0)

        # Run timered task(s) in main thread
        while True:
            self.send_heartbeat()
            time.sleep(FileNode.HEARTBEAT_INTERVAL) # Seconds

    def try_port(self):
        """
        Check if port is free, raise error if not
        :return:
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(self.address)
        except socket.error as e:
            s.close()
            raise OSError("Error in binding to socket %s:%i" % self.address) from e

    def register(self):
        """
        Send a HTTP GET request to register on name node
        http://127.0.0.1:10001/register/?ip_address=127.0.0.1&port=10002

        Wait for response from name node
        :return:
        """
        self.logger.info('Registering on name node %s:%i' % self.name_node_address)
        url = 'http://%s:%i/register' % self.name_node_address
        params = {
            'ip_address': self.address[0],
            'port': self.address[1]}
        try:
            response = requests.get(url=url, params=params)
        except socket.error as e:
            self.logger.info('Error in registering on name node %s:%i' % self.name_node_address)
            raise OSError("Error in registering on name node %s:%i" % self.name_node_address) from e
        self.logger.info('Registering done. Name node responded with %s' % str(response))

        self.send_filelist()

    def run_httpserver(self):
        """
        Run the HTTPServer
        :return:
        """
        server = HTTPServer(self.address, FileNodeHTTPRequestHandler)
        server.node = self    # <-- This allows the FileNodeHTTPRequestHandler to call this FileNode instance
        server.logger = self.logger
        self.logger.info('Listening to %s port %i' % self.address)
        server.serve_forever()

    def send_heartbeat(self):
        """
        Send a HTTP GET request to register on name node
        http://127.0.0.1:10001/heartbeat/?ip_address=127.0.0.1&port=10002
        Wait for response from name node
        :return:
        """
        self.logger.info('Sending heartbeat to name node %s port %i' % self.name_node_address)
        url = 'http://%s:%i/heartbeat' % self.name_node_address
        params = {
            'ip_address': self.address[0],
            'port': self.address[1]}
        try:
            # We don't want to wait for the response so we time-out quick
            requests.get(url=url, params=params, timeout=0.0000000001)
        except requests.exceptions.ReadTimeout:
            pass
        self.logger.info('Heartbeat sent')

    def store_file(self, file_name, file_content):
        """
        Store the file on disk
        :param file_name: Name of the file
        :param file_content: Content of the file
        :return:
        """
        self.logger.info('Storing file `%s` on disk' % file_name)

        # Store the file on disk
        with open(os.path.join(self.file_system_root, file_name), "wb") as f:
            f.write(file_content)
            f.close()

        # Send file list to name node
        self.send_filelist()

    def send_filelist(self):
        """
        Send a HTTP POST request to update the file list on name node
        http://127.0.0.1:10001/filelist/?ip_address=127.0.0.1&port=10002
        :return:
        """
        self.logger.info('Sending file list to name node %s port %i' % self.name_node_address)
        params = tuple([i for x in (self.name_node_address, self.address) for i in x])
        url = 'http://%s:%i/filelist?ip_address=%s&port=%i' % params
        data = {
            'ip_address': self.address[0],
            'port': self.address[1],
            'file_list': []}
        try:
            # We just want to send the request and not wait for the response => time-out quick
            requests.post(url=url, data=data, timeout=0.0000000001)
        except requests.exceptions.ReadTimeout:
            pass
        self.logger.info('File list sent')


class FileNodeHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def _message(self, content):
        return content.encode("utf8")  # NOTE: must return a bytes object!

    def do_GET(self):
        """
        Handle GET requests
         * Client: GET file
        :return:
        """
        self._set_headers()
        self.wfile.write(self._message('This is the file node %s:%i at %s' % (self.server.node.address[0], self.server.node.address[1], datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))))

    def do_PUT(self):
        """
        Handle PUT requests
         * Client: PUT file
        :return:
        """
        # Handle the request
        content_len = int(self.headers.get('Content-Length', 0))
        file_name = self.headers.get('File-Name', 0)
        file_content = self.rfile.read(content_len)
        self.server.node.store_file(file_name, file_content)  # <-- Here we call the fileNode
        # Send response to client
        self._set_headers()
        self.wfile.write(self._message('This is the file node at %s:%i at %s' % (self.server.node.address[0], self.server.node.address[1], datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))))
