import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import logging
from sys import stdout

from nameNode import NameNode
from fileNode import FileNode


def init_logging():
    log = logging.getLogger('')
    handler = logging.StreamHandler(stdout)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    log.setLevel(logging.DEBUG)
    log.addHandler(handler)
    return log


def get_port():
    return 10002


def parse_args():
    parser = argparse.ArgumentParser(description="Run name node of the distributed file system")
    parser.add_argument("-n", "--nodeType", default="nameNode", help="Type of the node/app: nameNode, fileNode, client")
    parser.add_argument("-i", "--ipAddress", default="127.0.0.1", help="Name node ip address")
    parser.add_argument("-p", "--port", default=None, type=int, help="Name node port number")
    args = parser.parse_args()
    return args.nodeType, args.ipAddress, args.port


def run(ip_address, port, handler_class, server_class=HTTPServer):
    server_address = (ip_address, port)
    httpd = server_class(server_address, handler_class)
    log.info('Listening to %s port %i', ip_address, port)
    httpd.serve_forever()


if __name__ == '__main__':
    log = init_logging()
    node_type, ip_address, port = parse_args()

    if node_type == "nameNode":
        log.info('Starting the Name Node')
        run(ip_address, (port or 10001), NameNode)
    elif node_type == "fileNode":
        log.info('Starting a File Node')
        run(ip_address, (port or get_port()), FileNode)
