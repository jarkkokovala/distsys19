### Project 1, a distributed system
Eeva-Maria Laiho, Jarkko Kovala, Paavo Hemmo

# Demo

https://www.youtube.com/watch?v=CDXFCeJbrEU

# Report

## Project Description (the project’s purpose and core functionality)

For the project 1 we decided to implement a distributed file system (DFS). A DFS is a system of multiple (hundreds, even thousands) nodes which are connected via a network. It's designed to store and manage a huge amount of files in a reliable, availale and fault-tolerant manner. A typical DFS implementation follows a master-worker architecture where a single master node manages a large set of worker nodes.

Our DFS implements of course only a tiny subset of the features of a real DFS and is more of a proof of concept than a working implementation. We implemented only the core components of a typical distributed file system: name node (master), file node (worker) and client application to connect to the dfs and basic communication between the components. Due to time constraints on the project we chose to focus on the task of reliably storing a file on the distributed file system.

## Documentation

* [System design](./documentation/specification.md)
* [Installation and execution guide](./documentation/installation.md)
* [Measurements, reliability and analysis](./documentation/measurements.md)


## Problems encountered, and lessons learned

Problems encountered

* Nothing major (if you don't count fighting with the semantics of the Python libraries used), our initial design worked quite well as originally planned.

Lessons learned

* Building distributed systems is tricky. You always get surprising failure scenarios and the complexity increases fast especially when you add parallel functionality, even a single thread in the system. 
* The system is always easier to build in your mind than in practise
* Try to keep things as simple as possible

## What's next?

* To make the system more reliable, the replication of files to different file nodes should happen dynamically. At the moment the replication is only done to 2 other file nodes, when adding the new file. This means that if the original, and the 2 file nodes containing the copy of the file, are all down, the file can not be retreived. The replication should therefore be done whenever a file node shuts down. This way the file could always be retrieved by the client.
