import math
import numpy as np
import pygame
import sys
import random

# Colors
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

PLAYER = 0
AI = 1

ROW_COUNT = 6
COLUMN_COUNT = 7
SQUARESIZE = 100
RADIUS = int(SQUARESIZE / 2) - 2

WINDOW_LENGTH = 4


def create_board():
    board = np.zeros((ROW_COUNT, COLUMN_COUNT))
    return board


def drop_piece(board, row, col, piece):
    board[row][col] = piece


def is_valid_location(board, col):
    return board[ROW_COUNT - 1][col] == 0


def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r


def print_board(board):
    print(np.flip(board, 0))


def winning_move(board, piece):
    # Check horizontal locations
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c + 1] == piece and board[r][c + 2] == piece and board[r][c + 3] == piece:
                return True
    # Check for vertical location
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r + 1][c] == piece and board[r + 2][c] == piece and board[r + 3][c] == piece:
                return True

    # Check for diagonal location
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r + 1][c + 1] == piece and board[r + 2][c + 2] == piece and board[r + 3][c + 3] == piece:
                return True
    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == piece and board[r - 1][c + 1] == piece and board[r - 2][c + 2] == piece and board[r - 3][c + 3] == piece:
                return True


def draw_board(board):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c * SQUARESIZE, (r + 1) * SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK,
                               (int(c * SQUARESIZE + SQUARESIZE / 2), int((r + 1) * SQUARESIZE + SQUARESIZE / 2)),
                               RADIUS)

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == 1:
                pygame.draw.circle(screen, RED, (int((c * SQUARESIZE + SQUARESIZE / 2)), height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
            elif board[r][c] == 2:
                pygame.draw.circle(screen, YELLOW, (int(c * SQUARESIZE + SQUARESIZE / 2), height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
    pygame.display.update()


def evaluate_window(window, piece):
    score = 0
    if window.count(1) == 3 and window.count(0) == 1:
        score -= 4
    elif window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(0) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(0) == 2:
        score += 10
    return score


def score_position(board, piece):
    score = -100000

    # Score centre column
    center_array = [int (i) for i in list(board[:, COLUMN_COUNT//2])]
    center_count = center_array.count(piece)
    score = center_count*6

    # Score Horizontal
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLUMN_COUNT-3):
            window = row_array[c:c+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Score Vertical
    for c in range(COLUMN_COUNT):
        column_array = [int(i) for i in list(board[:, c])]
        for r in range(ROW_COUNT-3):
            window = column_array[r:r+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Score +ve Slope Diagonal
    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+i][c] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    # Score -ve Slope Diagonal
    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+3-i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score


def is_terminal_node(board):
    return winning_move(board, 1) or winning_move(board, 2) or len(get_valid_location(board)) == 0


def minimax(board, depth, maxizingPlayer):
    valid_locations = get_valid_location(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, 2):
                return (None, 100000000)
            elif winning_move(board, 1):
                return (None, -100000000)
            else:  # Game is over no more valid moves
                return (None, 0)
        else: # depth is zero
            return (None, score_position(board, 2))
    if maxizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, 2)
            (c, new_score) = minimax(b_copy, depth-1, False)
            if new_score > value:
                value  = new_score
                column = col
        return column, value
    else: # minimizing player
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, 1)
            (c, new_score) = minimax(b_copy, depth-1, True)
            if new_score < value:
                value = new_score
                column = col
        return column, value


def get_valid_location(board):
    valid_location = []
    for col in range(COLUMN_COUNT):
        if is_valid_location(board, col):
            valid_location.append(col)

    return valid_location


def pick_best_move(board, piece):
    best_score = 0
    valid_location = get_valid_location(board)
    best_col = random.choice(valid_location)
    for col in valid_location:
        row = get_next_open_row(board, col)
        temp_board = board.copy()
        drop_piece(temp_board, row, col, piece)
        score = score_position(temp_board, piece)
        if score > best_score:
            best_score = score
            best_col = col

    return best_col


board = create_board()
game_over = False
turn = 0
pygame.init()
width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT + 1) * SQUARESIZE
size = (width, height)
screen = pygame.display.set_mode(size)
draw_board(board)
pygame.display.update()
myFont = pygame.font.SysFont("monospace", 75)
turn = random.randint(0, 1)

while not game_over:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.MOUSEMOTION:
            posX = event.pos[0]
            pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
            if turn == 0:
                pygame.draw.circle(screen, RED, (posX, int(SQUARESIZE / 2)), RADIUS)
        pygame.display.update()
        if event.type == pygame.MOUSEBUTTONDOWN:
            posX = event.pos[0]
            col = (posX // SQUARESIZE)
            if turn == PLAYER:
                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, 1)
                    if winning_move(board, 1):
                        pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                        label = myFont.render("Player 1 Won", 1, RED)
                        screen.blit(label, (40, 10))
                        game_over = True
                    turn += 1
                    turn %= 2
                    draw_board(board)
                    print_board(board)
                    if game_over:
                        pygame.time.wait(3000)
    if turn == AI and not game_over:
       # col = pick_best_move(board, 2)
        (col, score) = minimax(board, 4, True)
        if is_valid_location(board, col):
            pygame.time.wait(300)
            row = get_next_open_row(board, col)
            drop_piece(board, row, col, 2)
            if winning_move(board, 2):
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                label = myFont.render("Player 2 Won", 1, YELLOW)
                screen.blit(label, (40, 10))
                game_over = True
            turn += 1
            turn %= 2
            draw_board(board)
            print_board(board)
        if game_over:
            pygame.time.wait(3000)
