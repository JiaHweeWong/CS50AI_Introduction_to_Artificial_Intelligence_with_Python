"""
Tic Tac Toe Player
"""

import math
import copy

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
    if terminal(board) == True:
        return None
    else:
        x_count = 0
        o_count = 0
        # Counts the number of X and O
        for row in board:
            for elem in row:
                if elem == 'X':
                    x_count += 1
                elif elem == 'O':
                    o_count += 1
        # If number of X and O are the same, it is X turn
        if x_count == o_count:
            return 'X'
        elif x_count > o_count: # Otherwise, it is O turn
            return 'O'


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    set_of_actions = set() # set of actions
    # Iterate through the board
    for i in range(0,3):
        for j in range(0,3):
            if board[i][j] == EMPTY: # If cell is empty
                action = (i,j) # cell can be a possible action
                set_of_actions.add(action) # Add action to the set of actions
    return set_of_actions # return the set of actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    i = action[0] # first element of action tuple 
    j = action[1] # second element of action tuple
    curr_player = player(board) # check whose turn is it
 
    if board[i][j] == EMPTY: # if cell is empty
        new_board = copy.deepcopy(board) # deep copy a new board
        new_board[i][j] = curr_player # update the new board
        return new_board # return the resulting new board
    else: # else if cell is already filled
        raise ValueError # raise an error


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    curr_util = utility(board) # Obtain curr_utility of board

    if curr_util == 1: # if utility is 1
        return 'X' # X is the winner
    elif curr_util == -1: # if utility is -1
        return 'O' # O is the winner
    elif curr_util == 0: # if utility is 0
        return None # there are no winners
    


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # Check for winning conditions
    # Rows and Columns
    for i in range(0,3):
        # Row
        row = board[i]
        if (row[0] == row[1]) & (row[0] == row[2]) &\
            (row[0] != EMPTY): # Row
            return True
        # Column
        elif (board[0][i] == board[1][i]) &\
            (board[0][i] == board[2][i]) &\
                (board[0][i] != EMPTY): # Column
            return True
    # Diagonal
    if (board[0][0] == board[1][1]) &\
        (board[0][0] == board[2][2]) &\
            (board[0][0] != EMPTY):
        return True
    elif (board[0][2] == board[1][1]) &\
        (board[0][2] == board[2][0])  &\
            (board[0][2] != EMPTY):
        return True

    # If board has not met any winning condition

    # Check if all cells are filled
    all_cells_filled=True # assume all cells filled
    for i in range(0,3):
        for j in range(0,3):
            if board[i][j] == EMPTY: # if there exist empty cell
                all_cells_filled=False
     # if all cells filled but no winning condition, it must be a tie            
    if all_cells_filled == True:
        return True
    else: # else, game has not ended
        return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    # Check for winning conditions and player
    # Rows and Columns
    for i in range(0,3):
        # Row
        row = board[i]
        if (row[0] == row[1]) & (row[0] == row[2]) &\
            (row[0] != EMPTY): # Row
            if row[0] == 'X': # if X won the row
                return 1 # return 1
            elif row[0] == 'O': # if O won the row
                return -1 # return -1
        # Column
        elif (board[0][i] == board[1][i]) &\
            (board[0][i] == board[2][i]) &\
                (board[0][i] != EMPTY): # Column
            if board[0][i] == 'X': # if X won the column
                return 1
            elif board[0][i] == 'O': # if O won the column
                return -1
    # Diagonal
    if (board[0][0] == board[1][1]) &\
        (board[0][0] == board[2][2]) &\
            (board[0][0] != EMPTY):
        if board[0][0] == 'X': # if X won the diagonal
            return 1 # return 1
        elif board[0][0] == 'O': # if O won the diagonal
            return -1 # return -1
    elif (board[0][2] == board[1][1]) &\
        (board[0][2] == board[2][0])  &\
            (board[0][2] != EMPTY):
        if board[0][2] == 'X': # if X won the diagonal
            return 1 # return 1
        elif board[0][2] == 'O': # if O won the diagonal
            return -1 # return -1
    # if none of the winning conditions are met, game is a tie
    return 0

def max_value(board):
    if terminal(board):
        return utility(board)
    v = -1000
    for action in actions(board):
        v = max(v, min_value(result(board,action)))
    return v

def min_value(board):
    if terminal(board):
        return utility(board)
    v = 1000
    for action in actions(board):
        v = min(v, max_value(result(board,action)))
    return v

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    # Check whose turn is it
    curr_player = player(board)

    # if current player is X
    # player will try to maximize score
    if curr_player == 'X':
        v = -1000
        max_v = -1000
        for action in actions(board): # for action in set of actions
            v = min_value(result(board,action))
            if v > max_v:
                max_v = v
                x_action = action
        return x_action
    # elif current player is O
    # player will try to minimize score
    elif curr_player == 'O':
        v = 1000
        min_v = 1000
        for action in actions(board): # for action in set of actions
            v = max_value(result(board,action))
            if v < min_v:
                min_v = v
                o_action = action
        return o_action

