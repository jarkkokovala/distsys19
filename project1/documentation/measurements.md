
### Project 1, a distributed system
Eeva-Maria Laiho, Jarkko Kovala, Paavo Hemmo


# Measurements and reliability

## Emulating network latency

Network latency can be emulated with the [NetEm](https://wiki.linuxfoundation.org/networking/netem) tool. On Ubuntu the tool is pre-installed. To introduce mean 100msec latency on all network traffic (including local HTTP) command:

``` $ tc qdisc change dev lo root handle 1:0 netem delay 100ms ```

To introduce 10 msec variation and a correlation parameter:

``` $ tc qdisc change dev lo root handle 1:0 netem delay 100ms 10ms 25% ```

To introduce random packet loss where 2.5% of the packets are lost, command:

``` $ tc qdisc add dev lo root handle 1:0 netem delay 250msec loss 2.5% ```

To reset command:

``` $ tc qdisc del dev lo root```


## What is the average time for sending 50 messages between two nodes (random payload)?

## Choose 3 different fixed message sizes (payloads for min, average, max), what is the average time when sending 25 in each case?

## Choose a unique payload, e.g., average size, and then measure the inter arrival rate between messages?

## How reliable is your architecture? 

The architecture is able to achieve very high reliability. The data is replicated to a definable number of nodes, therefore the probability of losing data dependent on this number (probability of losing data = probability of losing a fileNode ^ number of replicas used).

The weak point in the architecture is the nameNode, on which all the other nodes are dependent. Since nameNode does not store persistent data, it doesn't affect the reliability but rather the availability of the system: if the nameNode is down, the data is still there but the system cannot be accessed. Due to simplicity of nameNode's function, it could trivially be replicated to mitigate these problems.

## What kind of applications can benefit from this architectural flavor?

This architecture could be used by any applications requiring reliable distributed access to data that doesn't change often. Writing data is not efficient due to the need to replicate and due to the nameNode being a bottleneck in this case, but the data could generally be read by an unlimited number of readers in this architecture as you can increase the number of fileNodes and replicas as necessary without limit. 

Distributed data mining (for example, MapReduce) would be an example of an application that would be perfect for this architecture.
