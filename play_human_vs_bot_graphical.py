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
PERFORM_BOT_ANALYSIS = False

def evaluate_human_move(prev_game, new_game):
    """Return bot commentary about the human's move."""
    s_prev = Solver(prev_game)
    human_win_before, _ = s_prev.best_moves(prev_game)

    s_new = Solver(new_game)
    human_win_after, _ = s_new.best_moves(new_game)

    if human_win_before and not human_win_after:
        return "Bot Analysis: That was a blunder!"
    elif not human_win_before and human_win_after:
        return "Bot Analysis: That was a good move!"
    elif human_win_after:
        return "Bot Analysis: That was an okay move..."
    else:
        return "Bot Analysis: Unsure..."

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
                pygame.draw.rect(screen, (0, 0, 0), rect, border_radius=10)  # collapsed tiles black
            else:
                pygame.draw.rect(screen, (255, 255, 255), rect, border_radius=10)  # normal tile white
                pygame.draw.rect(screen, GRID_COLOR, rect, 2, border_radius=10)  # grid lines

            # Draw player if they are on this tile
            for player in game.players:
                if player.position == (r, c):
                    shadow_offset = 4
                    pygame.draw.circle(screen, (0,0,0), 
                           (rect.centerx+shadow_offset, rect.centery+shadow_offset), 
                           CELL_SIZE//3)
                    color = PLAYER_COLORS[player.name]
                    pygame.draw.circle(screen, color, rect.center, CELL_SIZE // 3)

                    # Add text label inside circle
                    if player.name == "P1":
                        label = FONT.render("YOU", True, (255, 255, 255))
                    else:
                        label = FONT.render("BOT", True, (255, 255, 255))

                    label_rect = label.get_rect(center=rect.center)
                    screen.blit(label, label_rect)

            # Highlight possible moves if hovering over player
            if show_moves and (r, c) in possible_moves:
                glow_rect = rect.inflate(8, 8)
                pygame.draw.rect(screen, (200, 200, 50, 100), glow_rect, 4, border_radius=12)  # yellow border

            # Draw text inside tile if it exists
            if cell_val is not None:
                text = FONT.render(str(cell_val), True, TEXT_COLOR)
                # screen.blit(text, (x + CELL_SIZE//4, y + CELL_SIZE//4))
                screen.blit(text, (x + 5, y + 5))

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
                    # copy state for evaluation
                    import copy
                    prev_game = copy.deepcopy(game)

                    game.make_move(game.current_player, move)
                    game.next_player()
                    human_turn = False
                    bot_info = []

                    if PERFORM_BOT_ANALYSIS:
                        # evaluate the move
                        commentary = evaluate_human_move(prev_game, game)
                        bot_info.append(commentary)

        if not human_turn and not game.is_terminal and not waiting_for_input:
            s = Solver(game)
            win, moves = s.best_moves(game)
            if win:
                bot_move = random.choice(moves) if isinstance(moves, list) else moves
            else:
                bot_move = random.choice(game.get_current_player_moves())

            if not bot_info:
                bot_info = [
                    f"Bot thinking...",
                    f"Can win? {'Yes' if win else 'No'}",
                    f"Move chosen: {bot_move}",
                    f"States considered: {len(s.memoized_states.keys())}"
                ]
            else:
                bot_info.append("Bot thinking...")
                bot_info.append(f"Can win? {'Yes' if win else 'No'}")
                bot_info.append(f"Move chosen: {bot_move}")
                bot_info.append(f"States considered: {len(s.memoized_states.keys())}")

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
