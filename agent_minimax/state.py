# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent

from referee.game import \
    PlayerColor, Action, SpawnAction, SpreadAction, HexPos, HexDir
from referee.game.constants import *
from collections import defaultdict
from itertools import product

# CONSTANTS
INFINITY = float('inf')
WIN = 10000
LOSS = -10000
# Index for dictionary items
POS = 0
CELL = 1
# List of the HexPos of valid cells
CELLS = [HexPos(r, q) for (r, q) in list(product(list(range(7)), list(range(7))))]


class Cell:
    """
    The Cell class has two attributes: a color and a power. It is NOT
    associated with a HexPos by nature, but will be used in the board state
    dictionary as the values, while the HexPos will be the keys. Color will
    be a PlayerColor object, or None to represent an empty cell. Power will
    range from 0 to 6.
    """

    def __init__(self, color: PlayerColor | None = None, power: int = 0):
        self.color = color
        self.power = power

    def __repr__(self):
        return f"{self.color, self.power}"


class Board:
    """
    The Board class represents a board at a given time in the game. It has 3
    attributes: state, turn and turn_num. The state is a dictionary and
    provides the details of the pieces on the board. Turn tells us who's
    turn it is to play, while turn_num is the turn number. Therefore, if
    turn is RED, then the state will be a representation of the board before
    RED has played.
    """

    def __init__(self, initial_state: dict[HexPos, Cell] = {},
                 turn: PlayerColor = PlayerColor.RED,
                 turn_num: int = 0):
        self.state: dict[HexPos, Cell] = \
            defaultdict(lambda: Cell(None, 0))
        self.state.update(initial_state)
        self.turn = turn
        self.turn_num = turn_num

    def __repr__(self):
        return f"{self.state, self.turn_num, self.turn}"

    def copy(self):
        """
        The copy function allows for the copying of a Board object, preventing
        any undesired overwriting.
        """
        turn = self.turn
        turn_num = self.turn_num
        return Board(self.state.copy(), turn, turn_num)

    def totalCombPower(self):
        """
        totalCombPower calculates the total power that is on the board.
        """
        total = 0
        for cell in self.state.values():
            total += cell.power
        return total

    def colorPower(self, color: PlayerColor):
        """
        colorPower takes in a color variable and returns the total power for
        that color.
        """
        total = 0
        for cell in self.state.values():
            if cell.color == color:
                total += cell.power
        return total

    def boardInfo(self, color: PlayerColor):
        """
        boardInfo takes in a color variable, and using just one iteration,
        calculates all of the required data from the board's pieces for the
        evaluation function. This is the player's and opponent's power and total
        cells, as well as a list of the player's cells.
        """
        playerPower = 0
        oppPower = 0
        playerNumCells = 0
        oppNumCells = 0
        playerCells = []
        for item in self.state.items():
            if item[CELL].color == color:
                playerPower += item[CELL].power
                playerNumCells += 1
                playerCells.append(item)
            elif item[CELL].color == opponentColor(color):
                oppPower += item[CELL].power
                oppNumCells += 1
        return [playerPower, oppPower, playerNumCells, oppNumCells, playerCells]

    def colorCells(self, color: PlayerColor):
        """
        colorCells takes in a color variable, and returns a list of the pieces
        on the board that are of the correct color.
        """
        curr_state = self.state
        cells = []
        for item in curr_state.items():
            if item[CELL].color == color:
                cells.append(item)
        return cells

    def unsafePositions(self, color: PlayerColor):
        """
        unsafePositions takes in a color variable, which represents the player's
        color. It returns a list of positions that the opponent can potentially
        spread onto.
        """
        curr_state = self.state.copy()
        opp_cells = self.colorCells(color)
        for cell in opp_cells:
            pos = cell[POS]
            for dir in [HexDir.Down, HexDir.DownRight, HexDir.DownLeft,
                        HexDir.Up, HexDir.UpRight, HexDir.UpLeft]:
                simulateSpread(curr_state, color, pos, dir)
        return [x[POS] for x in curr_state.items() if x[CELL].color == color]

    def updateSpawn(self, color: PlayerColor, pos: HexPos):
        """
        updateSpawn updates the Board object such that the resulting board
        accounts for the spawning of a cell with color 'color' and position
        'pos'. Since an action was taken, we also need to switch turn to the
        other color, and increment turn_num by 1.
        """
        cell = Cell(color, 1)
        self.updatePlayer()
        self.turn_num += 1
        self.state[pos] = cell

    def updateSpread(self, color: PlayerColor, pos: HexPos, direction: HexDir):
        """
        updateSpread updates the Board object such that the resulting board
        accounts for the spread of a cell with color 'color', position 'pos' and
        direction 'direction. Since an action was taken, we also need to switch
        turn to the other color, and increment turn_num by 1.
        """
        power = self.state[pos].power
        self.state[pos] = Cell(None, 0)

        curr_pos = pos
        for _ in range(power):
            curr_pos += direction
            if self.state[curr_pos].power == MAX_CELL_POWER:
                self.state[curr_pos] = Cell(None, 0)
                continue
            else:
                self.state[curr_pos] = Cell(
                    color, self.state[curr_pos].power + 1)
        self.updatePlayer()
        self.turn_num += 1

    def updatePlayer(self):
        """
        updatePlayer updates the turn attribute to switch to the other player.
        """
        if self.turn == PlayerColor.RED:
            self.turn = PlayerColor.BLUE
        else:
            self.turn = PlayerColor.RED

    def getLegalActions(self):
        """
        getLegalActions returns a list of valid actions from the current board
        state. This is determined for whoever's turn it is, i.e. player's color
        = board.turn
        """
        if self.totalCombPower() >= MAX_TOTAL_POWER:
            spawn_actions = []
        else:
            spawn_cells = list(
                filter(lambda key: self.state[key].color is None, CELLS))
            spawn_actions = [SpawnAction(x) for x in spawn_cells]

        spread_cells = list(
            filter(lambda key: self.state[key].color == self.turn, CELLS))
        spread_dir = [HexDir.Down, HexDir.DownRight, HexDir.DownLeft,
                      HexDir.Up, HexDir.UpRight, HexDir.UpLeft]
        spread_actions = [SpreadAction(x, y) for (x, y) in
                          list(product(spread_cells, spread_dir))]

        return [x for x in spread_actions + spawn_actions]

    def move(self, action: Action):
        """
        move takes an action and updates the board accordingly.
        """
        match action:
            case SpawnAction(cell):
                self.updateSpawn(self.turn, cell)
            case SpreadAction(cell, dir):
                self.updateSpread(self.turn, cell, dir)

    def isGameOver(self):
        """
        isGameOver checks whether the game is over, either by max turns, or a
        player win. This code was taken from board.py in the referee module.
        """
        # Game can't be over within the first two turns.
        if self.turn_num < 2:
            return False

        return any([
            self.turn_num >= MAX_TURNS,
            self.colorPower(PlayerColor.RED) == 0,
            self.colorPower(PlayerColor.BLUE) == 0
        ])

    def gameResult(self) -> PlayerColor | None:
        """
        The player (color) who won the game, or None if no player has won. This
        function was taken from board.py in the referee module.
        """
        if not self.isGameOver():
            return None

        red_power = self.colorPower(PlayerColor.RED)
        blue_power = self.colorPower(PlayerColor.BLUE)

        if abs(red_power - blue_power) < WIN_POWER_DIFF:
            return None

        return (PlayerColor.RED, PlayerColor.BLUE)[red_power < blue_power]


class Node:
    """
    The Node class is defined to be the node in the minimax algorithm. It has
    three attributes: board, parent and parent_action. The board is the Board
    object at the node, and parent is the Board object that board came from.
    parent_action is the action taken to go from parent to board.
    """

    def __init__(self, board, parent=None, parent_action=None):
        self.board = board
        self.parent = parent
        self.parent_action = parent_action

    def __repr__(self) -> str:
        return f"{self.parent_action}"

    def copy(self):
        """
        The copy function allows for the copying of a Node object, preventing
        any undesired overwriting.
        """
        board = self.board.copy()
        if self.parent is None:
            parent = None
        else:
            parent = self.parent.copy()
        return Node(board, parent, self.parent_action)

    def getChildren(self):
        """
        getChildren returns a list of the children nodes of the current node.
        A children node is defined as a node which can be reached from the
        parent through one legal move.
        """
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
        """
        eval takes one optional argument: opponent. This is by default false,
        which says that we are currently the player, not the opponent. If
        opponent is true, then we need to account for that, since we always want
        to calculate the evaluation function with respect to the player.
        """
        # If opponent is false, it means we just played, and therefore, it's
        # actually now the opponent's turn.
        if opponent:
            opp_color = opponentColor(self.board.turn)
        else:
            opp_color = self.board.turn
        color = opponentColor(opp_color)
        turn_num = self.board.turn_num

        # Check for early exit from eval function if game is over
        if self.board.isGameOver():
            if self.board.gameResult() == color:
                return WIN
            elif self.board.gameResult() == opp_color:
                return LOSS
            else:
                return 0

        [player_power, opp_power, player_num_cells,
         opp_num_cells, player_cells] = self.board.boardInfo(color)

        diff_power = player_power - opp_power
        diff_num_cells = player_num_cells - opp_num_cells

        # safety - total power of safe cells
        safety = 0
        unsafe = self.board.unsafePositions(opp_color)
        for cell in player_cells:
            if cell[POS] not in unsafe:
                safety += cell[CELL].power

        if diff_num_cells > 0:
            safety_weight = 1 - diff_num_cells / player_num_cells
        else:
            safety_weight = 1.5

        # If there is only one piece left, and it's unsafe, then treat as a loss
        # already.
        if safety == 0 and player_num_cells <= 1 and turn_num >= 2:
            return LOSS
        return 0.5 * diff_power - opp_power + diff_num_cells - opp_num_cells + safety_weight * safety


def opponentColor(color: PlayerColor):
    """
    opponentColor takes a PlayerColor argument, and returns the other color.
    """
    return PlayerColor.RED if color == PlayerColor.BLUE else PlayerColor.BLUE


def simulateSpread(state: dict[HexPos, Cell], color: PlayerColor, pos: HexPos,
                   direction: HexDir):
    """
    simulateSpread is similar to updateSpread in that it will be determining
    a board after a spread move. However, only the positions spreaded onto
    are important, and hence it is a more relaxed function.
    """
    power = state[pos].power

    curr_pos = pos
    for _ in range(power):
        curr_pos += direction
        state[curr_pos] = Cell(
            color, state[curr_pos].power)


# The following alpha beta code (functions alpha_beta_search, max_value and
# min_value) was adapted from this blog:
# https://tonypoer.io/2016/10/28/implementing-minimax-and-alpha-beta-pruning-using-python/
def alpha_beta_search(node, depth):
    """
    alpha_beta_search is the starting function of the minimax algorithm, with
    alpha beta pruning. The recursion occurs in max_value and min_value. This
    function only ever runs for our player, and hence the first step is always a
    maximising player's move. It takes a node and a depth as arguments. The node
    is the root node, which represents the current board, while depth is how
    deep we want the minimax search to be.
    """
    best_val = -INFINITY
    beta = INFINITY

    start_node = node.copy()
    moves = node.board.getLegalActions()
    best_move = None
    for move in moves:
        node.board.move(move)
        value = min_value(node, best_val, beta, depth - 1)
        if value == WIN:
            return move
        elif value > best_val:
            best_val = value
            best_move = move
        node = start_node.copy()
    return best_move


def max_value(node, alpha, beta, depth):
    """
    max_value takes a node, an alpha and beta value as well as a depth. If the
    depth is 0 or the game is over, return the evaluation score. Otherwise,
    return the maximum value. With alpha-beta pruning, if the value reaches
    greater than beta, we can prune the rest of the nodes immediately.
    This function is for the maximising player.
    """
    if depth <= 0 or node.board.isGameOver():
        return node.eval(True)
    value = -INFINITY

    start_node = node.copy()
    moves = node.board.getLegalActions()
    for move in moves:
        node.board.move(move)
        value = max(value, min_value(node, alpha, beta, depth - 1))
        if value >= beta:
            node = start_node.copy()
            return value
        alpha = max(alpha, value)
        node = start_node.copy()
    return value


def min_value(node, alpha, beta, depth):
    """
    min_value takes a node, an alpha and beta value as well as a depth. If the
    depth is 0 or the game is over, return the evaluation score. Otherwise,
    return the minimum value. With alpha-beta pruning, if the value reaches
    less than alpha, we can prune the rest of the nodes immediately.
    This function is for the minimising player.
    """
    if depth <= 0 or node.board.isGameOver():
        return node.eval(False)
    value = INFINITY

    start_node = node.copy()
    moves = node.board.getLegalActions()
    for move in moves:
        node.board.move(move)
        value = min(value, max_value(node, alpha, beta, depth - 1))
        if value <= alpha:
            node = start_node.copy()
            return value
        beta = min(beta, value)
        node = start_node.copy()
    return value
