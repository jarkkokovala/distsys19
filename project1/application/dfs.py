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


def parse_args():
    parser = argparse.ArgumentParser(description="Run name node of the distributed file system")
    parser.add_argument("-n", "--nodeType", type=int, default=1, help="Type of the node: 1 = name node, 2 = file node, 3 = client app")
    parser.add_argument("-i", "--ipAddress", default="127.0.0.1", help="Name node ip address")
    parser.add_argument("-p", "--port", type=int, default=10001, help="Name node port number")
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

    if node_type == 1:
        log.info('Starting the Name Node')
        run(ip_address, port, NameNode)
    elif node_type == 2:
        log.info('Starting a File Node')
        run(ip_address, port, FileNode)
