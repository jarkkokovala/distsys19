
### Project 1, a distributed system
Eeva-Maria Laiho, Jarkko Kovala, Paavo Hemmo


# Measurements, reliability and analysis

## Emulating network latency

Network latency can be emulated with the [NetEm](https://wiki.linuxfoundation.org/networking/netem) tool. On Ubuntu the tool is pre-installed. The tool enables introducing netowork latency on all traffic including local HTTP.

To introduce network latency of 100ms with random variation sampled from normal distribution with mean 10ms command:

``` $ tc qdisc add dev lo root handle 1:0 netem delay 100ms 10ms distribution normal ```

To reset command:

``` $ tc qdisc del dev lo root```

## Measurements

For measuring system performance a small piece of instrumentation code was added to the client and nameNode. The system was timed at following points: 
1) client sends message to filenode, 
2) name node receives file list update request. 

Before measuring random latency (described above) was introduced in the system.

The random payloads (file content) were generated with the python3 lorem library.    

Measurement data can be found from the [data subdirectory](./data/mean_110ms_latency).

The measures displayed below are computed using the [measuring.ipynb](./data/mean_110ms_latency) Jupyter Notebook.

### What is the average time for sending 50 messages between two nodes (random payload)?

For this measurement the client sent 50 small (~4 kB) file upload requests to the dfs. 

### Choose 3 different fixed message sizes (payloads for min, average, max), what is the average time when sending 25 in each case?

For this measurement the client sent 50 small (~4 kB, of which top 25 were used), 25 medium (~400 kB) and 25 large (~4 MB) file upload requests to the dfs. 

### Choose a unique payload, e.g., average size, and then measure the inter arrival rate between messages?

For this measurement the client sent 50 small (~4 kB) file upload requests to the dfs. 

## How reliable is your architecture? 

The architecture is able to achieve very high reliability. The data is replicated to a definable number of nodes, therefore the probability of losing data dependent on this number (probability of losing data = probability of losing a fileNode ^ number of replicas used).

The weak point in the architecture is the nameNode, on which all the other nodes are dependent. Since nameNode does not store persistent data, it doesn't affect the reliability but rather the availability of the system: if the nameNode is down, the data is still there but the system cannot be accessed. Due to simplicity of nameNode's function, it could trivially be replicated to mitigate these problems.

## What kind of applications can benefit from this architectural flavor?

This architecture could be used by any applications requiring reliable distributed access to data that doesn't change often. Writing data is not efficient due to the need to replicate and due to the nameNode being a bottleneck in this case, but the data could generally be read by an unlimited number of readers in this architecture as you can increase the number of fileNodes and replicas as necessary without limit. 

Distributed data mining (for example, MapReduce) would be an example of an application that would be perfect for this architecture.
