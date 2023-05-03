# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent

from referee.game import \
    PlayerColor, Action, SpawnAction, SpreadAction, HexPos, HexDir
from referee.game.constants import *
from collections import defaultdict
from itertools import product
import random
import heapq

SPREAD_DIRECTIONS = [HexDir.Down, HexDir.DownRight, HexDir.DownLeft,
                     HexDir.Up, HexDir.UpRight, HexDir.UpLeft]

POS = 0
CELL = 1

class Cell:
    def __init__(self, color: PlayerColor | None = None, power: int = 0):
        self.color = color
        self.power = power

    def __repr__(self):
        return f"{self.color, self.power}"


class Board:
    def __init__(self, initial_state: dict[HexPos, Cell] = {},
                 turn: PlayerColor = PlayerColor.RED,
                 turn_num: int = 0):
        self.state: dict[HexPos, Cell] = \
            defaultdict(lambda: Cell(None, 0))
        self.state.update(initial_state)

        self.turn = turn
        self.turn_num = turn_num

    def __repr__(self):
        return f"{self.state}"

    def totalCombPower(self):
        # Calculate the total power of board
        total = 0
        for cell in self.state.values():
            total += cell.power
        return total

    def updateSpawn(self, color: PlayerColor, pos: HexPos):
        # update board for a spawn move
        cell = Cell(color, 1)
        new_state = self.state.copy()
        turn_num = 1 + self.turn_num
        turn = self.updatePlayer()
        new_state[pos] = cell
        return Board(new_state, turn, turn_num)

    def updateSpread(self, color: PlayerColor, pos: HexPos, direction: HexDir):
        # update board for spread move
        power = self.state[pos].power
        new_state = self.state.copy()
        new_state[pos] = Cell(None, 0)

        curr_pos = pos
        for _ in range(power):
            curr_pos += direction
            if new_state[curr_pos].power == MAX_CELL_POWER:
                new_state[curr_pos] = Cell(None, 0)
                continue
            else:
                new_state[curr_pos] = Cell(
                    color, new_state[curr_pos].power + 1)
        turn_num = 1 + self.turn_num
        turn = self.updatePlayer()

        return Board(new_state, turn, turn_num)

    def simulateSpawn(self, color: PlayerColor, pos: HexPos):
        # update board for a spawn move
        cell = Cell(color, 1)
        new_state = self.state.copy()
        new_state[pos] = cell
        return Board(new_state, self.turn, self.turn_num)

    def simulateSpread(self, color: PlayerColor, pos: HexPos, direction: HexDir):
        # update board for spread move
        power = self.state[pos].power
        new_state = self.state.copy()
        new_state[pos] = Cell(None, 0)

        curr_pos = pos
        for _ in range(power):
            curr_pos += direction
            if new_state[curr_pos].power == MAX_CELL_POWER:
                new_state[curr_pos] = Cell(None, 0)
                continue
            else:
                new_state[curr_pos] = Cell(
                    color, new_state[curr_pos].power + 1)

        return Board(new_state, self.turn, self.turn_num)

    def getLegalActions(self):
        # return a list of the valid moves from this board state for this player
        r = list(range(7))
        q = list(range(7))
        cells = list(product(r, q))
        cells = [HexPos(r, q) for (r, q) in cells]

        if self.totalCombPower() >= MAX_TOTAL_POWER:
            spawn_actions = []
        else:
            spawn_cells = list(
                filter(lambda key: self.state[key].color is None, cells))
            spawn_actions = [SpawnAction(x) for x in spawn_cells]

        heap_spawn = [(-self.simulateSpawn(self.turn, x.cell)._heuristic(), x) for x in spawn_actions]

        spread_cells = list(
            filter(lambda key: self.state[key].color == self.turn, cells))

        spread_actions = [SpreadAction(x, y) for (x, y) in
                          list(product(spread_cells, SPREAD_DIRECTIONS))]

        heap_spread = [(-self.simulateSpread(self.turn, x.cell, x.direction)._heuristic(), x) for x in
                       spread_actions]

        heap = heap_spread + heap_spawn
        print(heap)
        heapq.heapify(heap)

        return heap

    def updatePlayer(self):
        # iterate turns
        if self.turn == PlayerColor.RED:
            return PlayerColor.BLUE
        else:
            return PlayerColor.RED

    ## Heuristic methods
    def _heuristic(self):
        curr_colour = self.turn

        opp_colour = self.opponentColor()

        # if near end game, give more weighting to having more power i.e. give higher weighting to boards with more of our power
        player_power = self.colorPower(curr_colour)
        opp_power = self.colorPower(opp_colour)
        diff_power = player_power - opp_power

        player_num_cells = self.colorNumCells(curr_colour)
        opp_num_cells = self.colorNumCells(opp_colour)
        diff_num_cells = player_num_cells - opp_num_cells

        player_cells = self.colorCells(curr_colour)

        # safety - number of pieces and power of safe cells
        safety = 0
        unsafe = self.unsafePositions(opp_colour)
        for cell in player_cells:
            if cell[POS] not in unsafe:
                safety += cell[CELL].power

        # cells that can eat but not be eaten?

        if opp_power == 0:
            return 10000 + random.uniform(0.0, 0.1)
        if safety == 0:
            return -10000 + random.uniform(0.0, 0.1)
        return diff_power - opp_power + diff_num_cells - opp_num_cells + safety + random.uniform(0.0, 0.1)

    def colorNumCells(self, color: PlayerColor):
        # total number of cells for a color
        total = 0
        for cell in self.state.values():
            if cell.color == color:
                total += 1
        return total

    def colorCells(self, color: PlayerColor):
        # return a list of cells of a color
        curr_state = self.state
        cells = []
        for item in curr_state.items():
            if item[CELL].color == color:
                cells.append(item)
        return cells

    def colorPower(self, color: PlayerColor):
        # Calculate power for a color
        total = 0
        for cell in self.state.values():
            if cell.color == color:
                total += cell.power
        return total

    def unsafePositions(self, color: PlayerColor):
        curr_state = self.state.copy()
        opp_cells = self.colorCells(color)
        for cell in opp_cells:
            pos = cell[POS]
            for direction in [HexDir.Down, HexDir.DownRight, HexDir.DownLeft,
                      HexDir.Up, HexDir.UpRight, HexDir.UpLeft]:
                curr_state = simulateSpread2(curr_state, color, pos, direction)
        return [x[POS] for x in curr_state.items() if x[CELL].color == color]

    def opponentColor(self):
        return PlayerColor.RED if self.turn == PlayerColor.BLUE else PlayerColor.BLUE

    def _is_under_attack(self, base_cell):

        opp_colour = PlayerColor.RED if self.turn == PlayerColor.BLUE else PlayerColor.BLUE
        for direction in SPREAD_DIRECTIONS:
            key = base_cell[0]
            for radius in range(1, 7):

                key += direction

                if self.state[key].color == opp_colour and self.state[key].power >= radius:
                    return True

        return False

def simulateSpread2(state: dict[HexPos, Cell], color: PlayerColor, pos: HexPos,
                   direction: HexDir):
    # simulate spread to determine the locations that it can spread to
    power = state[pos].power
    new_state = state.copy()
    # new_state[pos] = Cell(None, 0)

    curr_pos = pos
    for _ in range(power):
        curr_pos += direction
        new_state[curr_pos] = Cell(
            color, new_state[curr_pos].power)

    return new_state
