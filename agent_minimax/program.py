# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent

from referee.game import \
    PlayerColor, Action, SpawnAction, SpreadAction, HexPos, HexDir
from referee.game.constants import *
from .state import Board, Node, alpha_beta_search
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
        curr_board = self._board
        board_copy = self._board.copy()
        node = Node(curr_board, None, None)
        depth = 3
        if referee["time_remaining"] < 80:
            depth = 2
        elif referee["time_remaining"] < 20:
            depth = 1
        move = alpha_beta_search(node, depth)
        self._board = board_copy
        return move


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
