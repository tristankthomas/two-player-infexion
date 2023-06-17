# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent

from referee.game import \
    PlayerColor, Action, SpawnAction, SpreadAction, HexPos, HexDir
from referee.game.constants import *
from collections import defaultdict
import numpy as np
from itertools import product
import time
import heapq
import random

TIME_LIMIT = 1

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
        return f"{self.state}"

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
                curr_state = simulateSpread(curr_state, color, pos, dir)
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


class MonteCarloTreeSearchNode:
    def __init__(self, board, parent=None, parent_action=None):
        self.board = board
        self.parent = parent
        self.parent_action = parent_action
        self.children = []
        self._n = 0
        self._wins = 0
        self._untried = self.untriedActions()

    def untriedActions(self):
        return self.board.getLegalActions()

    def expand(self):
        val = [evalFunction(board) for board in map(self.board.move, self._untried)]
        action = self._untried.pop(np.argmax(val))
        next_board = self.board.move(action)
        child_node = MonteCarloTreeSearchNode(
            next_board, parent=self, parent_action=action)
        self.children.append(child_node)
        return child_node

    def isTerminalNode(self):
        return self.board.isGameOver()

    def isFullyExpanded(self):
        return len(self._untried) == 0

    def rollout(self):
        current_rollout_board = self.board

        while not current_rollout_board.isGameOver():
            possible_moves = current_rollout_board.getLegalActions()

            action = self.rolloutPolicy(possible_moves)
            current_rollout_board = current_rollout_board.move(action)
        return current_rollout_board.gameResult()

    def rolloutPolicy(self, possible_moves):
        # eval_scores = [evalFunction(board) for board in map(self.board.move, possible_moves)]
        # return possible_moves[np.argmax(eval_scores)]
        return possible_moves[np.random.randint(len(possible_moves))]

    def backPropagate(self, result):
        self._n += 1
        if result == self.board.turn:
            self._wins += 1
        if self.parent:
            self.parent.backPropagate(result)

    def bestChild(self, c_param=0.1):
        # select the best child according to UCB1, only looks at expanded children
        choices_weights = [
            (c._wins / c._n) + c_param * np.sqrt((2 * np.log(self._n) / c._n)) + 0.01 * evalFunction(c.board) / (
                        c._n + 1) for c in self.children]
        return self.children[np.argmax(choices_weights)]

    def treePolicy(self):
        current_node = self
        while not current_node.isTerminalNode():

            if not current_node.isFullyExpanded():
                return current_node.expand()
            else:
                current_node = current_node.bestChild()
        return current_node

    def bestAction(self):
        start = time.time()
        count = 0
        while time.time() - start < TIME_LIMIT:
            v = self.treePolicy()
            reward = v.rollout()
            v.backPropagate(reward)
            count += 1
        print(count)

        return self.bestChild(c_param=0.).parent_action


def opponentColor(color: PlayerColor):
    return PlayerColor.RED if color == PlayerColor.BLUE else PlayerColor.BLUE


def simulateSpread(state: dict[HexPos, Cell], color: PlayerColor, pos: HexPos,
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


def evalFunction(board: Board):
    opp_color = board.turn  # because now the board will say it's the opponent's turn after we just made a move
    color = opponentColor(opp_color)
    turn_num = board.turn_num

    # if near end game, give more weighting to having more power i.e. give higher weighting to boards with more of our power
    player_power = board.colorPower(color)
    opp_power = board.colorPower(opp_color)
    if opp_power == 0:
        return 10000
    diff_power = player_power - opp_power

    player_num_cells = board.colorNumCells(color)
    opp_num_cells = board.colorNumCells(opp_color)
    diff_num_cells = player_num_cells - opp_num_cells

    player_cells = board.colorCells(color)

    # safety - number of pieces and power of safe cells
    safety = 0
    unsafe = board.unsafePositions(opp_color)
    for cell in player_cells:
        if cell[POS] not in unsafe:
            safety += cell[CELL].power

    possible_spread = len(board.unsafePositions(color))
    # cells that can eat but not be eaten?

    if safety == 0:
        return -10000
    return 0.5 * diff_power - opp_power + diff_num_cells - opp_num_cells + safety