### Project 1, a distributed system
Eeva-Maria Laiho, Jarkko Kovala, Paavo Hemmo

# System design

## Architecture

FILL IN HERE

## Processes / logical components

![System overview](./diagram1.png)
<!--https://www.lucidchart.com/documents/edit/c57d43b0-ede6-4ecb-a284-c0ca66047a74-->

### Client

* Client software
* Provides access to the distributed file system. 
* There can be many.

#### Communication

| Node from | | Node to | | |
| --- | --- | --- | --- | --- |
| Client | <--> | Name node | HTTP GET | Query file node ip-address ad port (for storing and reading a file). Wait for response. The name node responds with an ip-address and port number. |
| Client | <--> | File node | HTTP PUT | Store file on file node. Wait for reponse. File node responses when message is received. Not when file is stored. |
| Client | <--> | File node | HTTP GET |  Read file from file node. Wait for reponse. File node responses with the file. |

### Name Node

* Master node
* Single point of failure
* Always running/listening
* The client's and a file node's first point of contact
    * Informs the client which file node to use for PUT and GET
    * Adds the file node as part of the system (i.e. in the node list)
* Maintains a list of files
    * The file nodes inform the name node of their files when there are changes
* Maintains a list of file nodes
    * File nodes register themselves on the name node when they are started
    * File nodes send heartbeats to the name node

#### Communication

| Node from | | Node to | | |
| --- | --- | --- | --- | --- |
| Name node | --> | File node | HTTP POST | Tell the file node to replicate certain file to a certain other node. Do not wait for response. For fault tolerance when a file node has failed. |

### File Node

* Worker node
* There can be many
* Registers itself on the name node when started
* Handles storing the actual files


#### Communication

| Node from | | Node to | | |
| --- | --- | --- | --- | --- |
| File node | --> | Name node | HTTP POST | Register file node on name node. Do not wait or response. |
| File node | --> | Name node | HTTP POST | Send file list to name node. Do not wait or response. |
| File node | --> | Name node | HTTP POST | Send heartbeat to name node. Do not wait or response. |
| File node | --> | File node (replica) | HTTP POST | Send file for replication to another file node. Do not wait or response. |

## Communication

Communication between dfs client and nodes (name node, file nodes) as well as between nodes is handled via HTTP protocol. HTTP protocol was selected primarily for ease of implementation with python programmin language. In a real distributed file system a protocol other HTTP would be more suitable at least for short messages sent between the nodes like the heartbeat message sent from file nodes to the name node. 

The messages sent between client and nodes are described above in the processes section so that under each component a table of messages sent from the componenent are presented. The lists are not comprehensive list of all messages sent in a fully functioning distributed file system but a description of project state. 

An example communication sequence for storing a single file on the file system is decribed in the following picture.

![Sequence diagram for storing a file](./sequence1.png)
<!--https://www.lucidchart.com/documents/edit/66b3bccc-280f-48a8-b0be-1ba4f7274a9b-->




