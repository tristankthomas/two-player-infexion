# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent

from referee.game import \
    PlayerColor, Action, SpawnAction, SpreadAction, HexPos, HexDir
from referee.game.constants import *
from .state import Board
from random import choice
from itertools import product


# This is the entry point for your game playing agent.

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
        curr_state = self._board._state
        turn_num = self._board._turn_num
        spread_pieces = \
            [key for key in curr_state if curr_state[key].color == self._color]
        if turn_num < 2 or spread_pieces == []:
            move_type = 0
        elif self._board.totalCombPower() == MAX_TOTAL_POWER:
            move_type = 1
        else:
            move_type = choice([0, 1])

        if move_type:
            # spread
            spread_loc = choice(spread_pieces)
            spread_dir = choice([HexDir.Down, HexDir.DownRight, HexDir.DownLeft,
                                HexDir.Up, HexDir.UpRight, HexDir.UpLeft])
            return SpreadAction(spread_loc, spread_dir)
        else:
            # spawn
            r = list(range(7))
            q = list(range(7))
            locs = list(product(r, q))
            locs = [HexPos(r, q) for (r,q) in locs]
            locs = list(filter(lambda key: curr_state[key].color == None, locs))
            spawn_loc = choice(locs)
            return SpawnAction(spawn_loc)

    def turn(self, color: PlayerColor, action: Action, **referee: dict):
        """
        Update the agent with the last player's action.
        """
        match action:
            case SpawnAction(cell):
                # update Board
                self._board.updateSpawn(color, cell)
                print(f"Testing: {color} SPAWN at {cell}")
                pass
            case SpreadAction(cell, direction):
                self._board.updateSpread(color, cell, direction)
                print(f"Testing: {color} SPREAD from {cell}, {direction}")
                pass

        self._board._turn_num += 1
        self._board.updatePlayer()
