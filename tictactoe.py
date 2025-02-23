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
    num_x = sum(row.count(X) for row in board)
    num_o = sum(row.count(O) for row in board)
    
    return X if num_x == num_o else O                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    posible_actions = set()
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] == EMPTY:
                posible_actions.add((i,j))
    
    return posible_actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """

    if action == None: return board
    i,j = action
    if i<0 or i>2:
        raise Exception("Position out of range")
    if j<0 or j>2:
        raise Exception("Position out of range")
    if board[i][j] != EMPTY:
        raise Exception("Cell had already occupied")
    
    actual_player = player(board)
    
    new_board = copy.deepcopy(board)
    
    new_board[i][j] = actual_player

    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    for row in board:
        if row[0] == row[1] == row[2] and row[0] != EMPTY:
            return row[0]
    
    for colunm in range(3):
        if board[0][colunm]  == board[1][colunm] == board[2][colunm] and board[0][colunm] != EMPTY:
            return board[0][colunm]
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] != EMPTY:
        return board[0][0]
    if board[2][0] == board[1][1] == board[0][2] and board[1][1] != EMPTY:
        return board[1][1]
    
    return None
        

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) != None:
        return True
    
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] == EMPTY:
                return False
    
    return True



def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    result = winner(board)
    if result == X:
        return 1
    if result == O:
        return -1
    else:
        return 0
     


def min_value(board):
    if terminal(board) == True:
        return utility(board),None
    
    min_number = float("inf")
    
    best_act = None
    
    for action in actions(board):
        result_board = result(board,action)
        value, _ = max_value(result_board)
        
        if value < min_number:
            min_number = value
            best_act = action
        
    return min_number,best_act

def max_value(board):
    if terminal(board) == True:
        return utility(board),None
    
    max_number = -float("inf")
    
    best_act = None
    
    for action in actions(board):
        result_board = result(board,action)
        value, _ = min_value(result_board)
        
        if value > max_number:
            max_number = value
            best_act = action
        
    return max_number,best_act

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board) == True:
        return None
    
    actual_player = player(board)
    if actual_player == X:
        _, optimal = max_value(board)
    else:
        _, optimal = min_value(board)
    return optimal