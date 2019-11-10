from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import sys
import threading
import time
import utility.logger


class FileNode:
    HEARTBEAT_INTERVAL = 5
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

    def register(self):
        """
        Send a HTTP GET request to register on name server
        http://127.0.0.1:10001/register/?ip_address=127.0.0.1&port=10002

        Wait for response from name server
        :return:
        """
        FileNode.logger.info('Registering on name server %s port %i' % self.name_node_address)
        url = 'http://%s:%i/register' % self.name_node_address
        params = {
            'ip_address': self.address[0],
            'port': self.address[1]}
        response = requests.get(url=url, params=params)
        FileNode.logger.info('Registering done. Name Server responded with %s' % str(response))

    def run_httpserver(self):
        """
        Run the HTTPServer
        :return:
        """
        server = HTTPServer(self.address, FileNodeHTTPRequestHandler)
        server.node = self    ######  <== Setting the node argument allows the FileNodeHTTPRequestHandler to call this FileNode instance
        FileNode.logger.info('Listening to %s port %i' % self.address)
        server.serve_forever()

    def send_heartbeat(self):
        """
        Send a HTTP GET request to register on name server
        http://127.0.0.1:10001/heartbeat/?ip_address=127.0.0.1&port=10002
        Wait for response from name server
        :return:
        """
        FileNode.logger.info('Sending heartbeat to name server %s port %i' % self.name_node_address)
        url = 'http://%s:%i/heartbeat' % self.name_node_address
        params = {
            'ip_address': self.address[0],
            'port': self.address[1]}
        try:
            # We don't want to wait for the response so we time-out quick
            requests.get(url=url, params=params, timeout=0.0000000001)
        except requests.exceptions.ReadTimeout:
            pass
        FileNode.logger.debug('Heartbeat sent')

    def put_file(self, file_name, file_content):
        """
        Store the file on disk
        :param file_name: Name of the file
        :param file_content: Content of the file
        :return:
        """
        # Store the file on disk
        FileNode.logger.info('Storing file `%s` on disk' % file_name)

        # Send file list to server
        self.send_filelist()

    def send_filelist(self):
        """
        Send a HTTP POST request to update the file list on name server
        http://127.0.0.1:10001/filelist/?ip_address=127.0.0.1&port=10002
        :return:
        """
        FileNode.logger.info('Sending file list to name server %s port %i' % self.name_node_address)
        params = tuple([i for x in (self.name_node_address, self.address) for i in x])
        url = 'http://%s:%i/filelist?ip_address=%s&port=%i' % params
        data = {
            'ip_address': self.address[0],
            'port': self.address[1],
            'file_list': {}}
        try:
            # We don't want to wait for the response so we time-out quick
            requests.post(url=url, data=data, timeout=0.0000000001)
        except requests.exceptions.ReadTimeout:
            pass
        FileNode.logger.debug('Heartbeat sent')


class FileNodeHTTPRequestHandler(BaseHTTPRequestHandler):
    logger = utility.logger.get_logger('FileNodeHTTPRequestHandler')

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
        self.server.node.put_file(file_name, file_content)
        # Send response to client
        self._set_headers()
        self.wfile.write(self._message('This is the file node at %s:%i at %s' % (self.server.node.address[0], self.server.node.address[1], datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))))
