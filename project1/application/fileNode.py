import os
import socket
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import sys
import threading
import time
import pickle
import utility.logger
from urllib.parse import urlparse
import json


class FileNode:
    HEARTBEAT_INTERVAL = 5 # sec
    NETWORK_LATENCY = 100 # msec

    def __init__(self, ip_address, port, name_node_ip_address, name_node_port, file_system_root):
        """
        Initialize the node
        :param ip_address: Ip address
        :param port: Port number
        :param handler_class: Http handler class, should derive from BaseHTTPRequestHandler
        :param name_node_ip_address: ip address of the name node
        :param name_node_port: port of the name node
        :param file_system_root: directory where the files are stored for this node
        :return: void
        """
        self.address = (ip_address, port)
        self.name_node_address = (name_node_ip_address, name_node_port)
        self.file_system_root = file_system_root
        self.logger = utility.logger.get_logger('FileNode %s:%i' % self.address)
        sync_timeout = (100+FileNode.NETWORK_LATENCY)/1000
        self.sync_timeouts = (sync_timeout,sync_timeout)  # (Connection timeout, read timeout)
        self.async_timeouts = (sync_timeout, 0.000001)  # (Connection timeout, read timeout)
        if not os.path.exists(self.file_system_root):
            os.makedirs(self.file_system_root)

    def run(self):
        """
        Run the name node
        :return:
        """

        # Check that the port is not in use
        self.try_port()

        # Register on name node
        self.register()

        # Sen dinitial filelist to nameNode
        self.send_filelist()

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
        response = None
        try:
            try:
                response = requests.get(url=url, params=params, timeout=self.sync_timeouts)
            except (requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout):
                self.logger.info('Connect timeout, increase time and retry')
                timeouts = tuple([x*2 for x in self.sync_timeouts])
                requests.get(url=url, params=params, timeout=timeouts) # 500 msec
        except (requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout) as ex:
            self.logger.info('Error in registering on name node %s:%i' % self.name_node_address)
            raise OSError("Error in registering on name node %s:%i" % self.name_node_address) from ex
        self.logger.info('Registering done. Name node responded with %s' % str(response or ''))

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
            try:
                requests.get(url=url, params=params, timeout=self.async_timeouts)
            except requests.exceptions.ConnectTimeout:
                self.logger.info('Connect timeout, increase time and retry')
                timeouts = tuple([x*2 for x in self.async_timeouts])
                requests.get(url=url, params=params, timeout=timeouts) # 500 msec
        except requests.exceptions.ReadTimeout:
            pass
        self.logger.info('Heartbeat sent')

    def store_file(self, file_name, file_content, file_mtime, instrumentation_id=''):
        """
        Store the file on disk
        :param file_name: Name of the file
        :param file_content: Content of the file
        :param file_mtime: Last modification time for the file
        :param instrumentation_id: Internal id for measuring system performance
        :return:
        """
        self.logger.info('Storing file `%s` on disk' % file_name)

        # Store the file on disk
        with open(os.path.join(self.file_system_root, file_name), "wb") as f:
            f.write(file_content.encode())
            f.close()
            os.utime(os.path.join(self.file_system_root, file_name), (time.time(), file_mtime))

        # Send file list to name node
        self.send_filelist(instrumentation_id)

        # Replicate the file to N sibling nodes
        self.replicate_file(file_name, file_content, file_mtime, instrumentation_id)
    
    def store_replica(self, file_name, file_content, file_mtime, instrumentation_id=''):
        """
        Store a replica of file on disk
        :param file_name: Name of the file
        :param file_content: Content of the file
        :param file_mtime: Last modification time for the file
        :param instrumentation_id: Internal id for measuring system performance
        :return:
        """
        self.logger.info('Storing replica of file `%s` on disk' % file_name)

        # Store the file on disk
        with open(os.path.join(self.file_system_root, file_name), "wb") as f:
            f.write(file_content)
            f.close()
            os.utime(os.path.join(self.file_system_root, file_name), (time.time(), file_mtime))

        # Send file list to name node
        self.send_filelist(instrumentation_id)

    def read_file(self, file_name):
        self.logger.info('Reading file `%s` from disk' % file_name)
        with open(os.path.join(self.file_system_root, file_name), "r") as f:
            content = f.read()
            f.close()
        return content

    def send_filelist(self, instrumentation_id=''):
        """
        Send a HTTP POST request to update the file list on name node
        http://127.0.0.1:10001/filelist/?ip_address=127.0.0.1&port=10002
        :return:
        """
        self.logger.info('Sending file list to name node %s port %i' % self.name_node_address)
        params = tuple([i for x in (self.name_node_address, self.address) for i in x])
        url = 'http://%s:%i/filelist?ip_address=%s&port=%i' % params

        # Gather the list of files to send
        files = {}
        for filename in os.listdir(self.file_system_root):
            files[filename] = { 
                "mtime": os.path.getmtime(os.path.join(self.file_system_root, filename)),
                "size": os.path.getsize(os.path.join(self.file_system_root, filename))
            }
        data = {
            'ip_address': self.address[0],
            'port': self.address[1],
            'file_list': files,
            'instrumentation_id': instrumentation_id
        }
        try:
            # We just want to send the request and not wait for the response => time-out quick
            requests.post(url=url, json=data, timeout=0.0000000001)
        except requests.exceptions.ReadTimeout:
            pass

        # TODO: Code below does not work
        #try:
        #    try:
        #        requests.get(url=url, json=data, timeout=self.async_timeouts)
        #    except requests.exceptions.ConnectTimeout:
        #        self.logger.info('Connect timeout, increase time and retry')
        #        timeouts = tuple([x*2 for x in self.async_timeouts])
        #        requests.get(url=url, json=data, timeout=timeouts) # 500 msec
        #except requests.exceptions.ReadTimeout:
        #    pass
        self.logger.info('File list sent')
    
    def replicate_file(self, file_name, file_content, file_mtime, instrumentation_id=''):
        """
        Replicate a file by requesting replica hosts from nameNode and then storing a copy on each
        """

        url = 'http://%s:%i/replicanodes' % self.name_node_address
        params = {
            'ip_address': self.address[0],
            'port': self.address[1]}

        try:
            self.logger.info("Requesting replicas for file")

            response = requests.get(url=url, params=params)

            if response.status_code == 200:
                replicaNodes = response.json()

                # Save a copy to all the replica nodes
                for replicaNode in replicaNodes:
                    url = 'http://%s:%i/newreplica' % tuple(replicaNode)

                    jsondata = json.dumps({'content': file_content}).encode()
                    headers = {
                        'Content-Length': bytes(len(jsondata)),
                        'File-Name': file_name,
                        'File-Modification-Time': str(file_mtime),
                        'Instrumentation-Id': instrumentation_id
                    }

                    requests.put(url=url, data=jsondata, headers=headers)
        except requests.exceptions.ReadTimeout:
            pass
    

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
        query = urlparse(self.path)
        if query.path == "/file":
            file_name = os.path.basename(self.headers.get('File-Name', 0))
            content = self.server.node.read_file(file_name)

            self.send_response(200)
            self.send_header("Content-type", 'application/json; charset=utf-8')
            message = content.encode()
            self.send_header("Content-length", len(message))
            self.end_headers()
            self.wfile.write(message)

    def do_PUT(self):
        """
        Handle PUT requests
         * Client: PUT file
        :return:
        """

        query = urlparse(self.path)
        if query.path == "/newfile":
            # Handle the request
            content_len = int(self.headers.get('Content-Length', 0))
            file_name = os.path.basename(self.headers.get('File-Name', 0))
            file_mtime = float(self.headers.get('File-Modification-Time', 0))
            instrumentation_id = self.headers.get('Instrumentation-Id')

            file_content = json.loads(self.rfile.read(content_len).decode('utf-8'))["content"]

            # TODO: This method should be ASYNC so that we can quickly return a response to client
            self.server.node.store_file(file_name, file_content, file_mtime, instrumentation_id)  # <-- Here we call the fileNode

            # Send response to client
            self._set_headers()
            self.wfile.write(self._message('This is the file node at %s:%i at %s' % (self.server.node.address[0], self.server.node.address[1], datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))))
        elif query.path == "/newreplica":
            # Handle the request
            content_len = int(self.headers.get('Content-Length', 0))
            file_name = os.path.basename(self.headers.get('File-Name', 0))
            file_mtime = float(self.headers.get('File-Modification-Time', 0))
            instrumentation_id = self.headers.get('Instrumentation-Id')

            file_content = json.loads(self.rfile.read(content_len).decode('utf-8'))["content"].encode()

            # TODO: This method should be ASYNC so that we can quickly return a response to client
            self.server.node.store_replica(file_name, file_content, file_mtime, instrumentation_id)  # <-- Here we call the fileNode

            # Send response to client
            self._set_headers()
            self.wfile.write(self._message('This is the file node at %s:%i at %s' % (self.server.node.address[0], self.server.node.address[1], datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))))


