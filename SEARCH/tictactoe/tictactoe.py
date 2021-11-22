"""
Tic Tac Toe Player
"""
from abc import abstractproperty
import math, copy
X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    i = 0
    x_counter = 0
    o_counter = 0
    while i < 3:
        j = 0
        while j < 3:
            if board[i][j] == X:
                x_counter += 1
                j += 1
            elif board[i][j] == O:
                o_counter += 1
                j += 1
            else:
                j += 1
        i += 1
    return O if x_counter > o_counter else X


def actions(board):
    i = 0
    actions = set()
    while i < 3:
        j = 0
        while j < 3:
            if board[i][j] == None:
                actions.add((i, j))
            j += 1
        i += 1
    return actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    possible_actions = actions(board)
    board_copy = copy.deepcopy(board)
    if action not in possible_actions:
        print(action, possible_actions)
        raise ValueError
    else:
        board_copy[action[0]][action[1]] = player(board)
        return board_copy


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Check vertically
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2]:
            if board[i][0] == X:
                return X
            elif board[i][0] == O:
                return O
            else:
                return None
    # Check orizontally
    for j in range(3):
        if board[0][j] == board[1][j] == board[2][j]:
            if board[0][j] == X:
                return X
            elif board[0][j] == O:
                return O
            else:
                return None
    # Check diagonally
    if board[0][0] == board[1][1] == board[2][2]:
        if board[0][0] == X:
            return X
        elif board[0][0] == O:
            return O
        else:
            return None
    if board[2][0] == board[1][1] == board[0][2]:
        if board[2][0] == X:
            return X
        elif board[2][0] == O:
            return O
        else:
            return None
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if len(actions(board)) == 0 or winner(board) != None:
        return True
    else:
        return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if terminal(board):
        result = winner(board)
        if result == X:
            return 1
        elif result == O:
            return -1
        else:
            return 0 


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None
    else:
        if player(board) == X:
            print(max_value(board))
            return max_value(board)[1]
        elif player(board) == O:
            print(min_value(board))
            return min_value(board)[1]


def max_value(board):
    if terminal(board):
        return utility(board), None
    v = float("-inf")
    move = None  
    for action in actions(board):
        check_value, dummy = min_value(result(board, action))
        if check_value > v:
            v = check_value
            move = action
            if v == 1:
                return v, move
    return v, move


def min_value(board):
    if terminal(board):
        return utility(board), None
        
    v = float("inf")
    move = None       
    for action in actions(board):
        check_value, dummy = max_value(result(board, action))
        if check_value < v:
            v = check_value
            move = action
            if v == -1:
                return v, move
    return v, move