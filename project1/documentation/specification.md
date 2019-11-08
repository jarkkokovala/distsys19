# Specification

![Network diagram](./diagram1.png)
<!--https://www.lucidchart.com/documents/edit/c57d43b0-ede6-4ecb-a284-c0ca66047a74-->

## Logical Components

### Client

* Client software
* Provides access to the distributed file system. 

#### Communication

##### Client -> Name Node

* Get file list, response: list of files in the file system (SYNC)
* Get file node address, response: ip-address and port number (SYNC)

##### Client -> File Node

* PUT file, response: ok (SYNC)
* GET file, response: the file (SYNC)

### Name Node

* Master node
* Single point of failure
* Always running/listening
* The client's and a (novel) file server's first point of contact
    * Informs the client which file server to use for PUT and GET
    * Adds the (novel) file node as part of the system (i.e. in the node list)
* Maintains a list of files
    * The file nodes inform the name node of their files when there are changes
* Maintains a list of file nodes
    * File nodes register themselves on the name node when they are started
    * File nodes send heartbeats to the name node

##### Name Node -> Client

None

##### Name Node -> File Node

None

### File Node

* Worker node
* There can be many
* Registers itself on the name node when it's started
* Handles storing the actual files

##### File Node -> Client

None

##### File Node -> Name Node

* Register 
* Send file list 
* Send heartbeat 


