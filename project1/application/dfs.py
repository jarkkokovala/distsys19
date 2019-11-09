import argparse
import random
from nameNode import NameNode
from fileNode import FileNode
import utility

logger = utility.logger.get_logger('dfs')

def parse_args():
    """
    Parse command line arguments
    :return: node_type, ip_address, port, name_node_ip_address, name_node_port
    """
    parser = argparse.ArgumentParser(description="Run name node of the distributed file system")
    parser.add_argument("-t", "--nodeType", default="nameNode", help="Type of the node/app: nameNode, fileNode, client")
    parser.add_argument("-i", "--ipAddress", default="127.0.0.1", help="Node ip address")
    parser.add_argument("-p", "--port", default=None, type=int, help="Node port number")
    parser.add_argument("-nni", "--nameNodeIpAddress", default="127.0.0.1", help="Name node ip address")
    parser.add_argument("-nnp", "--nameNodePort", default=None, type=int, help="Name node port number")
    args = parser.parse_args()
    return args.nodeType, args.ipAddress, args.port, args.nameNodeIpAddress, args.nameNodePort


def get_port():
    """
    Get a random port number in range (10002, 11001)
    :return: Port number as integer
    """
    return 10001 + random.randint(1, 10) # 1000


if __name__ == '__main__':
    node_type, ip_address, port, name_node_ip_address, name_node_port = parse_args()
    if node_type == "nameNode":
        logger.info('Starting the Name Node')
        node = NameNode(ip_address, (port or 10001))
        node.run()
    elif node_type == "fileNode":
        logger.info('Starting a File Node')
        if not (name_node_ip_address and name_node_port):
            logger.error('Name node ip address and/or port undefined')
        else:
            while True:
                try:
                    node = FileNode(ip_address, (port or get_port()), name_node_ip_address, name_node_port, '../../dfs/' + str(port))
                    node.run()
                    break
                except OSError as ex:
                    logger.debug(ex.strerror)

