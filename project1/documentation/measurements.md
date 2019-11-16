
### Project 1, a distributed system
Eeva-Maria Laiho, Jarkko Kovala, Paavo Hemmo


# Measurements

## Emulating network latency

Network latency can be emulated with the [NetEm](https://wiki.linuxfoundation.org/networking/netem) tool. On Ubuntu the tool is pre-installed. To introduce mean 100msec latency with 10 msec variation and a correlation parameter on all network traffic (including local HTTP) command:

``` $ tc qdisc change dev lo root handle 1:0 netem delay 100ms 10ms 25% ```

To introduce random packet loss where 2.5% of the packets are lost, command:

``` $ tc qdisc add dev lo root handle 1:0 netem delay 250msec loss 2.5% ```

To reset command:

``` $ tc qdisc del dev lo root```


## What is the average time for sending 50 messages between two nodes (random payload)?

## Choose 3 different fixed message sizes (payloads for min, average, max), what is the average time when sending 25 in each case?

## Choose a unique payload, e.g., average size, and then measure the inter arrival rate between messages?

## How reliable is your architecture? 

## What kind of applications can benefit from this architectural flavor?
