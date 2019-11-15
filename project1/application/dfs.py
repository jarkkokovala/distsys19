import argparse
import random
import sys
import utility
from nameNode import NameNode
from fileNode import FileNode


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
    parser.add_argument("-r", "--fileSystemRoot", help="File system root")
    parser.add_argument("-nni", "--nameNodeIpAddress", default="127.0.0.1", help="Name node ip address")
    parser.add_argument("-nnp", "--nameNodePort", default=10001, type=int, help="Name node port number")
    parser.add_argument("-in", "--instrumentation", default=False, type=bool, help="Set True to start with instrumentation")
    args = parser.parse_args()
    return args.nodeType, args.ipAddress, args.port, args.nameNodeIpAddress, args.nameNodePort, args.fileSystemRoot, args.instrumentation


def get_port():
    """
    Get a random port number in range (10002, 11001)
    :return: Port number as integer
    """
    return 10001 + random.randint(1, 1000)


if __name__ == '__main__':
    node_type, ip_address, port, name_node_ip_address, name_node_port, file_system_root, instrumentation_enabled = parse_args()
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
                    p = port or get_port()
                    node = FileNode(ip_address, p, name_node_ip_address, name_node_port, file_system_root or ('../../dfsroot/' + str(p)))
                    node.run()
                    break  # Break out, we found a free port number
                except OSError as e:
                    if 'registering on name node' in str(e):
                        logger.info('It seems that there is a problem with the name node %s:%i.' % (name_node_ip_address, name_node_port))
                        break
                    else:
                        print(str(e))
            if i >= 9:
                logger.info('Unable to start the file node. The port number space may be congested.')
    except KeyboardInterrupt as ex:
        logger.info('A keyboard interrupt was detected')
    except:
        print("Unexpected error: %s", sys.exc_info()[0])
        raise
    logger.info('Exiting')
