
## Running the dfs

### Starting the name node

Cd to the program's main directory:

    $ cd <path-to-download-directory>/project1/application
    
You will need to install requests module:

```
pip install requests
```

Start the name node:

    $ python3 dfs.py

The name node will start listening to http requests at default address '127.0.0.1', port 10001. Non-default ip address and port number can be defined by passing parameters $-i$ (ip address) and $-p$ (port number).

#### Sending a request

After name node has been started it can be communicated with. To send a simple GET request, using a web browser navigate to:

    http://localhost:10001/

#### Stopping the node

You may stop program execution at any time by typing Ctrl+C.

### Starting a file node

Cd to the program's main directory:

    $ cd <path-to-download-directory>/project1/application

Start the file node:

    $ python3 dfs.py -t fileNode -p 10002 -nni '127.0.0.1' -nnp 10001
    
The file node will start listening to http requests at address '127.0.0.1', port 10002. If the port number is omitted the system will assign the file server a random port number in the range (10002, 11001). The file node will register itself on the name node at address '127.0.0.1', port 10001. If the name node address and port number parameters are omitted the system will use default values '127.0.0.1' and 10001.

#### Sending a request

After name node has been started it can be communicated with. To send a simple GET request, using a web browser navigate to:

    http://localhost:10002/
    
#### Stopping the node

You may stop program execution at any time by typing Ctrl+C.


