# Specification

![Network diagram][./diagram1.png]

## Logical Components

### Client

Role: Client software. Provides access to the distributed file system. 

#### Communication

##### Client -> Name Node

* Get file list, response: list of files in the file system (SYNC)
* Get file node address, response: ip-address and port number (SYNC)

##### Client -> File Node

* Put file, response: ok (SYNC)
* Get file, response: the file (SYNC)

### Name Node

Role: Master node. Always running/listening. The client's and a (novel) file server's first point of contact. Maintains a list of files and file nodes.

##### Name Node -> Client

None

##### Name Node -> File Node

None

### File Node

Role: Worker node. Registers itself to the Name Node when it's started. There can be many. Handles storing the actual files. 

##### File Node -> Client

None

##### File Node -> Name Node

* Register
* Send file list
* Send heartbeat


