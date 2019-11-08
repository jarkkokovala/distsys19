# Project 1

## Running the dfs

### Start the name node

Cd to the program's main directory:

    $ cd <path-to-download-directory>/project1/application

Execute the program:

    $ python3 dfs.py -port 10001

The name node will start listening to http requests at address '127.0.0.1', port 10001. If the port number is omitted the default port number 10001 is used.

#### Sending a request

After name node has been started it can be queried using for example a web browser. To query the name node type:

    $ http://localhost:10001/
    
in your browser.

#### Stopping

You may stop program execution at any time by typing Ctrl+C.


### Start the file node

Cd to the program's main directory:

    $ cd <path-to-download-directory>/project1/application

Execute the program:

    $ python3 dfs.py -n fileNode -port 10002
    
The file node will start listening to http requests at address '127.0.0.1', port 10002. If the port number is omitted the system will assign the file server a port number in the range (10002, 10010).

#### Sending a request

After name node has been started it can be queried using for example a web browser. To query the name node type browse to:

    $ http://localhost:10002/
    
#### Stopping

You may stop program execution at any time by typing Ctrl+C.


