import inspect
import json
import utility.logger
import sys
import threading
import random
import time

from http.server import BaseHTTPRequestHandler, HTTPServer
from random import shuffle
from urllib.parse import urlparse, parse_qs, unquote
from utility.instrumentation import instrumentation
import requests


class NameNode:
    FILENODE_TIMEOUT = 15 # Seconds after we time out a filenode if it hasn't sent a heartbeat
    REPLICA_N = 1

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

    def get_fileNode(self, file_name='',  instrumentation_id=''):
        # If file_name is left empty (or None), just return a random fileNode
        """
        Return a fileNode's address and port
        :param addressFilter: address to filter as a tuple of (ip_address, port_number)
        :return: a fileNode with the file of name file_name or a random fileNode
        """
        ret = None
        instrumentation.warning("%s;%s;%s" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, instrumentation_id))
        with self.fileNodes_lock:
            if len(self.fileNodes) > 0:
                if file_name:
                    # Select the filenode which contains the file
                    for i in range(len(list(self.fileNodes.keys()))):
                        key = list(self.fileNodes.keys())[i]
                        if file_name in self.fileNodes[key]['files']:
                            ret = key
                            break
                else:
                    # Select a random fileNode
                    ret = list(self.fileNodes.keys())[random.randint(0, len(list(self.fileNodes.keys())) - 1)]
            else:
                ret = None
        print(ret)
        return ret

    def get_replica_fileNodes(self, filter_address, instrumentation_id=''):
        """
        Get a list of replica fileNodes
        :param addressFilter: address to filter from the list as a tuple of (ip_address, port_number)
        :return: First NameNode.REPLICA_N fileNodes in random order
        """
        instrumentation.warning("%s;%s;%s" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, instrumentation_id))

        self.logger.info('Sending replicas for %s port %i', filter_address[0], filter_address[1])

        with self.fileNodes_lock:
            ret = list(self.fileNodes)
        
        shuffle(ret)

        return [x for x in ret if not x == filter_address][:NameNode.REPLICA_N]

    def do_heartbeat(self, addrport):
        """
        Process a heartbeat from a fileNode
        :param addrport: Address and port of the node as tuple
        :return:
        """

        self.logger.info('Received heartbeat from %s port %i', addrport[0], addrport[1])
        with self.fileNodes_lock:
            self.fileNodes[addrport]["last_heartbeat"] = time.time()

    def update_filelist(self, addrport, files, instrumentation_id=''):
        """
        Update the filelist for a fileNode
        :param addrport: Address and port of the node as tuple
        :param files: the new filelist
        :return:
        """
        self.logger.info('Updating filelist for %s port %i, %i files', addrport[0], addrport[1], len(files))
        with self.fileNodes_lock:
            self.fileNodes[addrport]["files"] = files
        instrumentation.warning("%s;%s;%s" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, instrumentation_id))
    
    def get_filelist(self):
        if len(self.fileNodes) > 0:
            all_files = []
            for i in range(len(list(self.fileNodes.keys()))):
                key = list(self.fileNodes.keys())[i]
                all_files = all_files + list(self.fileNodes[key]['files'])
            return list(set(all_files))
        else:
            return None

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
        url = urlparse(self.path)
        query = parse_qs(url.query)
        instrumentation_id = self.headers.get('Instrumentation-Id')
        response_code = 200

        #print(url, query, instrumentation_id)

        address = None
        if "ip_address" in query and "port" in query:
            address = (query["ip_address"][0], int(query["port"][0]))

        file_name = None
        if "file_name" in query:
            file_name = query["file_name"][0]

        response_body = None

        if url.path == "/register": # Register request from filenode
            if address:
                self.server.node.register_fileNode(address)
            else:
                response_code = 400
        elif url.path == "/heartbeat": # Heartbeat request from filenode
            if address:
                self.server.node.do_heartbeat(address)
            else:
                response_code = 400
        elif url.path == "/filenode": # Get fileNode request from client
            file_node = self.server.node.get_fileNode(file_name, instrumentation_id)
            if file_node:
                # TODO: Return fileNode address to client
                print(file_node)
                data = {
                    'ip_address': file_node[0],
                    'port': file_node[1]
                }
                self.send_response(200)
                self.send_header("Content-type", 'application/json; charset=utf-8')
                message = json.dumps(data).encode()
                self.send_header("Content-length", len(message))
                self.end_headers()
                self.wfile.write(message)
            else:
                response_code = 400
        elif url.path == "/replicanodes": # Return replica node address(es) for fileNode
            if address:
                replica_nodes = self.server.node.get_replica_fileNodes(address, instrumentation_id)
                if replica_nodes:
                    response_body = json.dumps(replica_nodes).encode()
                else:
                    response_code = 400
            else:
                response_code = 400
        elif url.path == "/filelist":
            files = self.server.node.get_filelist()
            if files:
                self.send_response(200)
                self.send_header("Content-type", 'application/json; charset=utf-8')
                message = json.dumps(files).encode()
                self.send_header("Content-length", len(message))
                self.end_headers()
                self.wfile.write(message)
            else:
                response_code = 400
        else:
            response_code = 404 # Not found

        if not response_code == 200:
            self.send_error(response_code)
            self.end_headers()

        self._set_headers()

        if response_body:
            self.wfile.write(response_body)

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
