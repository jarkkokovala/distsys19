
### Project 1, a distributed system
Eeva-Maria Laiho, Jarkko Kovala, Paavo Hemmo


# Measurements

Network latency can be emulated with the NetEm tool. On Ubuntu the tool is pre-installed. To introduce 100msec latency on all traffic (including local HTTP) command:

``` $tc qdisc add dev lo root handle 1:0 netem delay 100msec ```

To reset command:

``` $tc qdisc del dev lo root```


## What is the average time for sending 50 messages between two nodes (random payload)?

## Choose 3 different fixed message sizes (payloads for min, average, max), what is the average time when sending 25 in each case?

## Choose a unique payload, e.g., average size, and then measure the inter arrival rate between messages?

## How reliable is your architecture? 

## What kind of applications can benefit from this architectural flavor?
