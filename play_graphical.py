import pygame
import random
from collapsi.configs.configs import *
from collapsi.modules.game import *
from collapsi.utilities.solver import *
from collapsi.utilities.vprint import vprint

# --------------------------
# Pygame setup
# --------------------------
pygame.init()
CELL_SIZE = 80
BOARD_COLOR = (30, 30, 30)
GRID_COLOR = (0, 0, 0)
PLAYER_COLORS = {"P1": (200, 50, 50), "P2": (50, 50, 200)}
TEXT_COLOR = (0, 0, 0)
SCREEN_MARGIN = 50
FONT = pygame.font.SysFont(None, 30)

def draw_board(screen, game, bot_info=None, mouse_pos=None):
    screen.fill(BOARD_COLOR)
    rows, cols = len(game.board), len(game.board[0])

    # Determine hover highlight
    show_moves = True
    possible_moves = []
    if mouse_pos:
        mx, my = mouse_pos
        row = (my - SCREEN_MARGIN) // CELL_SIZE
        col = (mx - SCREEN_MARGIN) // CELL_SIZE
        if (row, col) == game.current_player.position:
            show_moves = True
            possible_moves = game.get_current_player_moves()

    for r in range(rows):
        for c in range(cols):
            x = SCREEN_MARGIN + c * CELL_SIZE
            y = SCREEN_MARGIN + r * CELL_SIZE
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

            cell_val = game.board[r][c]
            if getattr(cell_val, "collapsed", False):
                pygame.draw.rect(screen, (0, 0, 0), rect)  # collapsed tiles black
            else:
                pygame.draw.rect(screen, (255, 255, 255), rect)  # normal tile white
                pygame.draw.rect(screen, GRID_COLOR, rect, 2)  # grid lines

            # Draw player if they are on this tile
            for player in game.players:
                if player.position == (r, c):
                    pygame.draw.circle(screen, PLAYER_COLORS[player.name], rect.center, CELL_SIZE//3)

            # Highlight possible moves if hovering over player
            if show_moves and (r, c) in possible_moves:
                pygame.draw.rect(screen, (200, 200, 50, 100), rect, 4)  # yellow border

            # Draw text inside tile if it exists
            if cell_val is not None:
                text = FONT.render(str(cell_val), True, TEXT_COLOR)
                screen.blit(text, (x + CELL_SIZE//4, y + CELL_SIZE//4))

    # Display current player
    if game.current_player.name == "P1":
        player_text = FONT.render(f"Your Turn", True, (255,255,255))
    else:
        player_text = FONT.render(f"Bot's Turn", True, (255,255,255))
    screen.blit(player_text, (SCREEN_MARGIN, SCREEN_MARGIN + rows*CELL_SIZE + 10))

    # Draw bot info
    if bot_info:
        for i, line in enumerate(bot_info):
            text = FONT.render(line, True, (255,255,255))
            screen.blit(text, (SCREEN_MARGIN, SCREEN_MARGIN + rows*CELL_SIZE + 40 + i*25))

    pygame.display.flip()


def get_cell_from_mouse(pos, game):
    x, y = pos
    row = (y - SCREEN_MARGIN) // CELL_SIZE
    col = (x - SCREEN_MARGIN) // CELL_SIZE
    if 0 <= row < len(game.board) and 0 <= col < len(game.board[0]):
        return (row, col)
    return None


# --------------------------
# Main loop
# --------------------------
if __name__ == "__main__":
    rows, cols = 6, 7
    screen = pygame.display.set_mode((cols*CELL_SIZE + 2*SCREEN_MARGIN,
                                      rows*CELL_SIZE + 3*SCREEN_MARGIN))
    pygame.display.set_caption("Collapsi - Graphical Version")

    game = GameState(num_players=2)
    game.players[0].name = "P1"
    game.players[1].name = "P2"

    clock = pygame.time.Clock()
    running = True
    human_turn = True
    bot_info = []

    waiting_for_input = False  # flag for end-of-game

    while running:
        mouse_pos = pygame.mouse.get_pos()
        draw_board(screen, game, bot_info, mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if waiting_for_input:
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    running = False
                continue  # skip normal gameplay if waiting

            if human_turn and event.type == pygame.MOUSEBUTTONDOWN:
                move = get_cell_from_mouse(event.pos, game)
                if move in game.get_current_player_moves():
                    game.make_move(game.current_player, move)
                    game.next_player()
                    human_turn = False
                    bot_info = []

        if not human_turn and not game.is_terminal and not waiting_for_input:
            s = Solver(game)
            win, moves = s.best_moves(game)
            if win:
                bot_move = random.choice(moves) if isinstance(moves, list) else moves
            else:
                bot_move = random.choice(game.get_current_player_moves())

            bot_info = [
                f"Bot thinking...",
                f"Can win? {'Yes' if win else 'No'}",
                f"Move chosen: {bot_move}",
                f"States considered: {len(s.memoized_states.keys())}"
            ]

            pygame.time.wait(500)
            game.make_move(game.current_player, bot_move)
            game.next_player()
            human_turn = True

        if game.is_terminal and not waiting_for_input:
            bot_info.append("Game Over!")
            if game.current_player.name == "P1":
                bot_info.append("BOT WINS")
            else:
                bot_info.append("YOU WIN")
            waiting_for_input = True  # now wait for player input

        clock.tick(30)
