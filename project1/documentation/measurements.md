
### Project 1, a distributed system
Eeva-Maria Laiho, Jarkko Kovala, Paavo Hemmo


# Measurements, reliability and analysis

## Measurements

For measuring system performance a small piece of instrumentation code was added to the client and nameNode. The system was timed at following points: 
1) client sends a message to the filenode, 
2) name node receives file list update request and has added the file in the list. 

Client code was altered so that a simple loop was introduced to perform the measurements. Random payloads (=file content) were generated with the python3 lorem library. The measuring cod is not included in the repository.

To simulate a more realistic setting random network latency (described below) was introduced in the system before measuring, 

Measurement data can be found from the [data](./data/mean_110ms_latency) subdirectory.

The measures presented below were computed using the [measuring.ipynb](./measuring.ipynb) Jupyter Notebook.

### Emulating network latency

Network latency can be emulated with the [NetEm](https://wiki.linuxfoundation.org/networking/netem) tool. On Ubuntu the tool is pre-installed. The tool enables introducing netowork latency on all traffic including local HTTP.

To introduce network latency of 100ms with random variation sampled from normal distribution with mean 10ms command:

``` $ tc qdisc add dev lo root handle 1:0 netem delay 100ms 10ms distribution normal ```

To reset command:

``` $ tc qdisc del dev lo root```

### What is the average time for sending 50 messages between two nodes (random payload)?

For this measurement the client sent 50 small (~4 kB) file upload requests to the dfs. 

Instead of measuring communication between the nodes we measure system performance from the client's point of view. We ask 'when is the file available' / 'when is the file reliably available'  (i.e. stored on primary/replica file server).

The average time for the two events:

* primary file stored and available:
    * mean: 0.750013
    * std: 0.023479
    * min: 0.696061
    * max: 0.795315
* replica file stored and available: 
    * mean: 1.814501
    * std: 0.039680
    * min: 1.738792
    * max: 1.923551

### Choose 3 different fixed message sizes (payloads for min, average, max), what is the average time when sending 25 in each case?

For this measurement the client sent 50 small (~4 kB, of which top 25 were used), 25 medium (~400 kB) and 25 large (~4 MB) file upload requests to the dfs. 

For this measurement we report total time i.e. the time when the replica file has been stored and is available. 

The average time for the three payloads:

* small: 
    * mean: 1.814501
    * std: 0.039680
    * min: 1.738792
    * max: 1.923551
* medium: 
    * mean: 1.826728
    * std: 0.038115
    * min: 1.749864
    * max: 1.882395
 * large: 
    * mean: 5.409429
    * std: 0.055534
    * min: 5.314126
    * max: 5.559336

### Choose a unique payload, e.g., average size, and then measure the inter arrival rate between messages?

For this measurement the client sent 25 medium (~400 kB) file upload requests to the dfs. 

The inter-arrival rate for primary and replica file list update requests are:

* primary:
    * mean: 2.276277
    * std: 0.476096
    * min: 2.310353
    * max: 2.472921
* replica: 
    * mean: 2.274086
    * std: 0.476313
    * min: 2.280142
    * max: 2.446791

## How reliable is your architecture? 

The architecture is able to achieve very high reliability. The data is replicated to a definable number of nodes, therefore the probability of losing data dependent on this number (probability of losing data = probability of losing a fileNode ^ number of replicas used).

The weak point in the architecture is the nameNode, on which all the other nodes are dependent. Since nameNode does not store persistent data, it doesn't affect the reliability but rather the availability of the system: if the nameNode is down, the data is still there but the system cannot be accessed. Due to simplicity of nameNode's function, it could trivially be replicated to mitigate these problems.

## What kind of applications can benefit from this architectural flavor?

This architecture could be used by any applications requiring reliable distributed access to data that doesn't change often. Writing data is not efficient due to the need to replicate and due to the nameNode being a bottleneck in this case, but the data could generally be read by an unlimited number of readers in this architecture as you can increase the number of fileNodes and replicas as necessary without limit. 

Distributed data mining (for example, MapReduce) would be an example of an application that would be perfect for this architecture.
