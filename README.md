# distsys19
Distributed systems harjoitusryhmä

## Group

Eeva-Maria Laiho, Jarkko Kovala, Paavo Hemmo

## Tasks

## Mitä (ainakin) puuttuu:

- tiedostosolmu: 
    - ~~tiedoston tallennus levylle~~, 
    - ~~tiedostoluettelon lähetys nimipalvelusolmulle~~, 
    - tiedostojen replikointi (riittää varmaan, että replikoidaan yhdelle sisarsolmulle): Jarkko
- nimipalvelisolmu
    - ~~tiedostosolmun rekisteröiminen~~, 
    - ~~solmun kaatumisen havaitseminen (heartbeat)~~, 
    - ~~tiedostoluettelon hallinta~~, 
    - clientin pyyntöihin vastaaminen: Paavo
- clientin toteutus: Paavo
- videodemo. 
- mitoitus: Eeva-Maria

### Report: 

1) A thorough final report about the project’s purpose and core functionality; 
2) your system design using the 3 principles from the lectures (architecture, processes, communication), 
3) problems encountered, and lessons learned: Jarkko, Eeva-Maria, Paavo
4) Instructions for installation and execution: Eeva-Maria
5) Answer the following questions with your implementation: 
    - What is the average time for sending 50 messages between two nodes (random payload)? 
    - Choose 3 different fixed message sizes (payloads for min, average, max), what is the average time when sending 25 in each case? 
    - Choose a unique payload, e.g., average size, and then measure the inter arrival rate between messages? 
    - How reliable is your architecture? What kind of applications can benefit from this architectural flavor?


