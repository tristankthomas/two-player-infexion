# Two-Player Infexion Board Game Agent
This project was created as part of an artificial intelligence subject in a group of 2 and required creating agents that can play the board game Infextion (described below). The referee module was provided by the subject and used to mediate the two agents competing against each other. There were four agents created; two simple ones (greedy and random) and two more complex ones (minimax and Monte Carlo tree search). 

To compare the agents performances a bash script was written to generate data which was then processed using the provided Jupyter notebook. From these tests it was found that the minimax agent with alpha beta pruning performed the best. There was a time constraint of 180 seconds so this minimax agent adjusted its search depth as time ran out. 
## Rules
This game is set on a 7 x 7 hexagonally tiled, infinitely repeating board. Two players (red and blue) compete, with the goal of taking control of all 'tokens' on the board. Each hexagonal cell on the board may be empty or have a stack of tokens called its **Power** (between 1 and 6), that is controlled by a particular player. 

The game starts with an empty board and there are two possible moves available in a given turn, **Spawn** and **Spread**, that change the game state in different ways. 
- **Spawn** allows a token to be generated on any empty cell (causing a **Power** of 1) on the condition that the total **Power** of all cells is less than 49.
- **Spread** allows the **Power** of a token stack to be 'spread' in a consecutive line of adjacent cells (six possible spread directions in the hexagonal grid), allowing for opponents stacks to be 'taken'.

The game ends when one player takes control of all opponents tokens on the board. If there has been 343 turns without a winner being declared, the player with the highest total **Power** is declared the winner.


