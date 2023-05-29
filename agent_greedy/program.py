# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent

from referee.game import \
    PlayerColor, Action, SpawnAction, SpreadAction, HexPos, HexDir
from referee.game.constants import *
from .state import Board
from random import choice
from itertools import product
import heapq
import numpy as np


# This is the entry point for your game playing agent. Currently the agent
# simply spawns a token at the centre of the board if playing as RED, and
# spreads a token at the centre of the board if playing as BLUE. This is
# intended to serve as an example of how to use the referee API -- obviously
# this is not a valid strategy for actually playing the game!

class Agent:
    def __init__(self, color: PlayerColor, **referee: dict):
        """
        Initialise the agent.
        """
        self._color = color
        self._board = Board()
        match color:
            case PlayerColor.RED:
                print("Testing: I am playing as red")
            case PlayerColor.BLUE:
                print("Testing: I am playing as blue")

    def action(self, **referee: dict) -> Action:
        """
        Return the next action to take.
        """
        curr_state = self._board.state
        turn_num = self._board.turn_num

        if turn_num < 2:
            # spawn
            r = list(range(7))
            q = list(range(7))
            locs = list(product(r, q))
            locs = [HexPos(r, q) for (r, q) in locs]
            locs = list(filter(lambda key: curr_state[key].color is None, locs))
            spawn_loc = choice(locs)
            return SpawnAction(spawn_loc)
        else:
            # either
            possible_moves = self._board.getLegalActions()
            return heapq.heappop(possible_moves)[1]

    def turn(self, color: PlayerColor, action: Action, **referee: dict):
        """
        Update the agent with the last player's action.
        """
        match action:
            case SpawnAction(cell):
                # update Board
                self._board = self._board.updateSpawn(color, cell)
                # print(f"Testing: {color} SPAWN at {cell}")
                pass
            case SpreadAction(cell, direction):
                self._board = self._board.updateSpread(color, cell, direction)
                # print(f"Testing: {color} SPREAD from {cell}, {direction}")
                pass
