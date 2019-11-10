import argparse
import random
import sys

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
    parser.add_argument("-nnp", "--nameNodePort", default=10001, type=int, help="Name node port number")
    args = parser.parse_args()
    return args.nodeType, args.ipAddress, args.port, args.nameNodeIpAddress, args.nameNodePort


def get_port():
    """
    Get a random port number in range (10002, 11001)
    :return: Port number as integer
    """
    return 10001 + random.randint(1, 1000)


if __name__ == '__main__':
    node_type, ip_address, port, name_node_ip_address, name_node_port = parse_args()
    try:
        if node_type == "nameNode":
            logger.info('Starting the Name Node')
            node = NameNode(ip_address, (port or 10001))
            node.run()
        elif node_type == "fileNode":
            logger.info('Starting a File Node')
            i = 0
            while i < 10:  # We don't want to try for ever
                i += 1
                try:
                    p = (port or get_port())
                    print(p)
                    node = FileNode(ip_address, p, name_node_ip_address, name_node_port, '../../dfs/' + str(port))
                    node.run()
                    break  # Break out, we found a free ip port
                except OSError:   # We don't really need to handle errors, just retry
                    pass
            if i >= 9:
                logger.info('It seems that the port number space is congested')
    except KeyboardInterrupt as ex:
        logger.info('A keyboard interrupt was detected')
    except:
        print("Unexpected error: %s", sys.exc_info()[0])
        raise
    logger.info('Exiting')
