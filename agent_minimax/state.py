# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent

from referee.game import \
    PlayerColor, Action, SpawnAction, SpreadAction, HexPos, HexDir
from referee.game.constants import *
from collections import defaultdict
from itertools import product
import time
import heapq
import random

TIME_LIMIT = 1
DEPTH_LIMIT = 2
INFINITY = float('inf')

POS = 0
CELL = 1

BOARD = 1


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
        return f"{self.state, self.turn_num}"

    def totalCombPower(self):
        # Calculate the total power of board
        total = 0
        for cell in self.state.values():
            total += cell.power
        return total

    def colorPower(self, color: PlayerColor):
        # Calculate power for a color
        total = 0
        for cell in self.state.values():
            if cell.color == color:
                total += cell.power
        return total

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

    def unsafePositions(self, color: PlayerColor):
        curr_state = self.state.copy()
        opp_cells = self.colorCells(color)
        for cell in opp_cells:
            pos = cell[POS]
            for dir in [HexDir.Down, HexDir.DownRight, HexDir.DownLeft,
                        HexDir.Up, HexDir.UpRight, HexDir.UpLeft]:
                simulateSpread(curr_state, color, pos, dir)
        return [x[POS] for x in curr_state.items() if x[CELL].color == color]

    def updateSpawn(self, color: PlayerColor, pos: HexPos):
        # update board for a spawn move
        cell = Cell(color, 1)
        new_state = self.state.copy()
        turn = self.updatePlayer()
        turn_num = 1 + self.turn_num
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
        turn = self.updatePlayer()
        turn_num = 1 + self.turn_num
        return Board(new_state, turn, turn_num)

    def isPieceTaken(self, color: PlayerColor, pos: HexPos, direction: HexDir):
        # update board for spread move
        power = self.state[pos].power
        new_state = self.state.copy()
        new_state[pos] = Cell(None, 0)
        takes_piece = False

        curr_pos = pos
        for _ in range(power):
            curr_pos += direction
            if new_state[curr_pos].power == MAX_CELL_POWER:
                new_state[curr_pos] = Cell(None, 0)
                continue
            else:
                if new_state[curr_pos].color == self.turn:
                    takes_piece = True

                new_state[curr_pos] = Cell(
                    color, new_state[curr_pos].power + 1)

        return takes_piece

    def updatePlayer(self):
        # iterate turns
        if self.turn == PlayerColor.RED:
            return PlayerColor.BLUE
        else:
            return PlayerColor.RED

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

        spread_cells = list(
            filter(lambda key: self.state[key].color == self.turn, cells))
        spread_dir = [HexDir.Down, HexDir.DownRight, HexDir.DownLeft,
                      HexDir.Up, HexDir.UpRight, HexDir.UpLeft]
        spread_actions = [SpreadAction(x, y) for (x, y) in
                          list(product(spread_cells, spread_dir))]

        return [x for x in spread_actions + spawn_actions]

    def move(self, action: Action):
        match action:
            case SpawnAction(cell):
                return self.updateSpawn(self.turn, cell)
            case SpreadAction(cell, dir):
                return self.updateSpread(self.turn, cell, dir)

    def isGameOver(self):
        # taken from the board.py in referee module
        if self.turn_num < 2:
            return False

        return any([
            self.turn_num >= MAX_TURNS,
            self.colorPower(PlayerColor.RED) == 0,
            self.colorPower(PlayerColor.BLUE) == 0
        ])

    def gameResult(self) -> PlayerColor | None:
        """
        The player (color) who won the game, or None if no player has won.
        """
        # taken from the board.py in referee module
        if not self.isGameOver():
            return None

        red_power = self.colorPower(PlayerColor.RED)
        blue_power = self.colorPower(PlayerColor.BLUE)

        if abs(red_power - blue_power) < WIN_POWER_DIFF:
            return None

        return (PlayerColor.RED, PlayerColor.BLUE)[red_power < blue_power]

    def eval(self):
        opp_color = self.turn  # because now the board will say it's the opponent's turn after we just made a move
        color = opponentColor(opp_color)
        turn_num = self.turn_num

        # if near end game, give more weighting to having more power i.e. give higher weighting to boards with more of our power
        player_power = self.colorPower(color)
        opp_power = self.colorPower(opp_color)
        if opp_power == 0:
            return 10000
        diff_power = player_power - opp_power

        player_num_cells = self.colorNumCells(color)
        opp_num_cells = self.colorNumCells(opp_color)
        diff_num_cells = player_num_cells - opp_num_cells

        player_cells = self.colorCells(color)

        # safety - number of pieces and power of safe cells
        safety = 0
        unsafe = self.unsafePositions(opp_color)
        for cell in player_cells:
            if cell[POS] not in unsafe:
                safety += cell[CELL].power

        # possible_spread = len(self.board.unsafePositions(color))
        # cells that can eat but not be eaten?

        if safety == 0:
            return -10000
        return 0.5 * diff_power - opp_power + diff_num_cells - opp_num_cells + safety


class Node:
    def __init__(self, board, parent=None, parent_action=None):
        self.board = board
        self.parent = parent
        self.parent_action = parent_action

    def __repr__(self) -> str:
        return f"{self.parent_action}"

    def simulateMove(self, move: Action):
        self.parent = self.board
        self.board = self.board.move(move)
        self.parent_action = move

    def copy(self):
        return Node(self.board, self.parent, self.parent_action)

    def getChildren(self):
        children = []
        if self.board.isGameOver():
            return children
        actions = self.board.getLegalActions()
        for action in actions:
            next_board = self.board.move(action)
            child_node = Node(next_board, parent=self, parent_action=action)
            children.append(child_node)
        return children

    def eval(self, opponent=False):
        if opponent:
            opp_color = opponentColor(self.board.turn)
        else:
            opp_color = self.board.turn  # because now the board will say it's the opponent's turn after we just made a move
        color = opponentColor(opp_color)
        turn_num = self.board.turn_num

        # if near end game, give more weighting to having more power i.e. give higher weighting to boards with more of our power
        player_power = self.board.colorPower(color)
        opp_power = self.board.colorPower(opp_color)
        if opp_power == 0 and turn_num < 2:
            return 10000
        diff_power = player_power - opp_power

        player_num_cells = self.board.colorNumCells(color)
        opp_num_cells = self.board.colorNumCells(opp_color)
        diff_num_cells = player_num_cells - opp_num_cells

        player_cells = self.board.colorCells(color)

        # safety - number of pieces and power of safe cells
        safety = 0
        unsafe = self.board.unsafePositions(opp_color)
        for cell in player_cells:
            if cell[POS] not in unsafe:
                safety += cell[CELL].power

        safety_weight = 1

        if safety == 0 and player_num_cells == 0 and turn_num >= 2:
            return -10000 + random.uniform(0.0, 0.1)
        return 0.5 * diff_power - opp_power + diff_num_cells - opp_num_cells + safety_weight * safety + random.uniform(0.0, 0.1)


def opponentColor(color: PlayerColor):
    return PlayerColor.RED if color == PlayerColor.BLUE else PlayerColor.BLUE


def simulateSpread(state: dict[HexPos, Cell], color: PlayerColor, pos: HexPos,
                   direction: HexDir):
    # simulate spread to determine the locations that it can spread to
    power = state[pos].power
    # new_state[pos] = Cell(None, 0)

    curr_pos = pos
    for _ in range(power):
        curr_pos += direction
        state[curr_pos] = Cell(
            color, state[curr_pos].power)


def alpha_beta_search(node, depth=0):
    best_val = -INFINITY
    beta = INFINITY

    children = node.getChildren()
    best_node = None
    for child in children:
        value = min_value(child, best_val, beta, depth + 1)
        if value > best_val:
            best_val = value
            best_node = child
    print("AlphaBeta:  Utility Value of Root Node: = " + str(best_val))
    return best_node.parent_action


def max_value(node, alpha, beta, depth=0):
    if node.board.isGameOver() or depth >= DEPTH_LIMIT:
        return node.eval(True)
    value = -INFINITY

    children = node.getChildren()
    for child in children:
        value = max(value, min_value(child, alpha, beta, depth + 1))
        if value >= beta:
            return value
        alpha = max(alpha, value)
    return value


def min_value(node, alpha, beta, depth=0):
    if node.board.isGameOver() or depth >= DEPTH_LIMIT:
        return node.eval(False)
    value = INFINITY

    children = node.getChildren()
    for child in children:
        value = min(value, max_value(child, alpha, beta, depth + 1))
        if value <= alpha:
            return value
        beta = min(beta, value)
    return value
