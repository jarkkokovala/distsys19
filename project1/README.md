# Project 1

## Running the dfs

### Start the name node

Cd to the program's main directory:

    $ cd <path-to-download-directory>/project1/application

Execute the program:

    $ python3 dfs.py -port 10001

The name node will start listening to '127.0.0.1' at port 10001. If the port number is omitted the default port 10001 is used.

You may stop program execution at any time by typing Ctrl+C.


### Start the file node

Cd to the program's main directory:

    $ cd <path-to-download-directory>/project1/application

Execute the program:

    $ python3 dfs.py -n fileNode -port 10002
    
The file node will start listening to '127.0.0.1' at port 10002. 

You may stop program execution at any time by typing Ctrl+C.


