# distsys19
Distributed systems harjoitusryhmä

## Group

Eeva-Maria Laiho, Jarkko Kovala, Paavo Hemmo

## Tasks

### Part 3

![Kumpula traffic lights](kumpula.png)

The picture depicts a petri net model for Kumpula traffic lights.

The lights have three possible states:

* Initial state in which traffic is possible in the north-south direction
* Second state in which traffic is possible in the south to side road and side road to south directions
* Third state in which traffic is possible in the north to side road direction

The lights are green in the directions allowed and red in other directions, lights are orange when changing state from green to red but orange lights are not modelled to keep the graph size down. As depicted in the picture in the task description, traffic in the side road to north direction is not possible.

The singular token depicts change of the lights between the three states. The "capacity" places depict the capacity to accept cars in a direction, and are refilled by the light turning green in that particular direction. Since WoPeD does not support a reset arc, it is not possible to model resetting the capacities: instead in this graph the weighted arc to the "capacity" place means setting the number of tokens to the amount determined by the weight.

The "inbound" places depict cars coming from each direction. A new car coming to the intersection would be represented by adding a token in an "inbound" place. The "car from" transitions represent cars moving from a direction to another: this transition is possible only if the light is green in that direction, as it consumes and produces a token with a two-way arc to the appropriate "green" place. It also consumes a token from the "capacity" state, limiting the number of cars that may proceed in that particular direction.


