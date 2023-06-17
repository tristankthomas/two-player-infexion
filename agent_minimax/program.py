# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent

from referee.game import \
    PlayerColor, Action, SpawnAction, SpreadAction, HexPos, HexDir
from referee.game.constants import *
from .state import Board, Node, alpha_beta_search
from random import choice
from itertools import product


class Agent:
    def __init__(self, color: PlayerColor, **referee: dict):
        """
        Initialise the agent, with a new Board object.
        """
        self._color = color
        self._board = Board()

    def action(self, **referee: dict) -> Action:
        """
        Using the current board and taking into account the remaining resources,
        run an alpha-beta search to determine the next move to take, and return
        the action.
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
        Update the agent's Board object to be up to date with its own actions as
        well as the opponent's actions.
        """
        match action:
            case SpawnAction(cell):
                self._board.updateSpawn(color, cell)
                pass
            case SpreadAction(cell, direction):
                self._board.updateSpread(color, cell, direction)
                pass
