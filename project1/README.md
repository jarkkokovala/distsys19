### Project 1, a distributed system
Eeva-Maria Laiho, Jarkko Kovala, Paavo Hemmo

# Report

## Project Description (the project’s purpose and core functionality)

For the project 1 we decided to implement a distributed file system (DFS). A DFS is a system of multiple (hundreds to hundred thousands) computers which are connected via a network. It's designed to store and manage a huge amount of files in a reliable, availale and fault-tolerant manner. A typical DFS implementation follows a master-worker architecture where a single master node manages a large set of worker nodes.

Our DFS implements of course only a tiny subset of the features of a real DFS and is more of a proof of concept than a working implementation. We have implemented only the core components of a typical distributed file system: master (the name node), worker (the file node) and client and basic communication between the components. Due to the limited time that we had for the project we chose to focus on the task of reliably storing a file on the distributed file system in our implementation and also our documentation.

## Documentation

* [System design](./documentation/specification.md)
* [Installation and execution guide](./documentation/installation.md)
* [Measurements](./documentation/measurements.md)


## Problems encountered, and lessons learned

Problems encountered

*

Lessons learned

* 
