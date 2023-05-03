# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent

from referee.game import \
    PlayerColor, Action, SpawnAction, SpreadAction, HexPos, HexDir
from referee.game.constants import *
from collections import defaultdict

class Cell:
    def __init__(self, color: PlayerColor|None = None, power: int = 0):
        self.color = color
        self.power = power


class Board:
    def __init__(self, initial_state: dict[HexPos, Cell] = {}):
        self.state: dict[HexPos, Cell] = \
            defaultdict(lambda: Cell(None, 0))
        self.state.update(initial_state)
        self._turn: PlayerColor = PlayerColor.RED
        self.turn_num: int = 0

    def totalCombPower(self):
        # Calculate the total power of board
        total = 0
        for cell in self.state.values():
            total += cell.power
        return total

    def updateSpawn(self, color: PlayerColor, pos: HexPos):
        cell = Cell(color, 1)
        self.state[pos] = cell

    def updateSpread(self, color: PlayerColor, pos: HexPos, direction: HexDir):
        power = self.state[pos].power

        self.state[pos] = Cell(None, 0)

        curr_pos = pos
        for i in range(power):
            curr_pos += direction
            if self.state[curr_pos].power == MAX_CELL_POWER:
                self.state[curr_pos] = Cell(None, 0)
                continue
            else:
                self.state[curr_pos] = Cell(
                    color, self.state[curr_pos].power + 1)

    def updatePlayer(self):
        if self._turn == PlayerColor.RED:
            self._turn == PlayerColor.BLUE
        else:
            self._turn == PlayerColor.RED
        