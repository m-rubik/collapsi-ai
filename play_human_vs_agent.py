import pygame
import torch
import numpy as np
from collapsi.modules.card import Card
from collapsi.modules.game import GameState
from collapsi.modules.agent import DQNAgent, encode_state, encode_action, decode_action

# --- Constants ---
TILE_SIZE = 100
WIDTH, HEIGHT = 4 * TILE_SIZE, 4 * TILE_SIZE
FPS = 60
MODEL_PATH = "collapsi_model.pth"

# --- Drawing Helpers ---
def draw_text(screen, text, position, font_size=24):
    font = pygame.font.SysFont(None, font_size)
    img = font.render(str(text), True, (0, 0, 0))
    rect = img.get_rect(topleft=position)
    screen.blit(img, rect)

def draw_board(screen, game):
    for r in range(4):
        for c in range(4):
            tile = game.board[r][c]
            rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            color = (150, 150, 150) if tile.collapsed else (255, 255, 255)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (0, 0, 0), rect, 2)
            label = tile.value if not tile.collapsed else "X"
            text_pos = (c * TILE_SIZE + 5, r * TILE_SIZE + 5)
            draw_text(screen, label, text_pos)

    for player in game.players:
        if player.active:
            r, c = player.position
            pos = (c * TILE_SIZE + TILE_SIZE // 2, r * TILE_SIZE + TILE_SIZE // 2)
            color = (255, 0, 0) if player.name == 'Human' else (0, 0, 255)
            pygame.draw.circle(screen, color, pos, 15)

# --- Main Game Loop ---
def play_human_vs_ai():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Collapsi: Human vs AI")
    clock = pygame.time.Clock()

    game = GameState(num_players=2)
    game.players[0].name = 'Human'
    game.players[1].name = 'AI'
    current_player = game.players[0]

    agent = DQNAgent()
    agent.model.load_state_dict(torch.load(MODEL_PATH))
    agent.model.eval()

    running = True
    while running:
        screen.fill((180, 180, 180))
        draw_board(screen, game)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return

        if current_player.name == 'Human':
            legal_moves = game.get_player_moves(current_player)
            selected = None
            while selected is None:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        mx, my = pygame.mouse.get_pos()
                        r, c = my // TILE_SIZE, mx // TILE_SIZE
                        if (r, c) in legal_moves:
                            selected = (r, c)
                            break
                clock.tick(FPS)

            game.make_move(current_player, selected)

        elif current_player.name == 'AI':
            legal_moves = game.get_player_moves(current_player)
            if not legal_moves:
                current_player.active = False
                break

            state_vec = encode_state(game, agent_name='AI')
            legal_indices = [encode_action(r, c) for (r, c) in legal_moves]
            q_vals = agent.model(torch.tensor(state_vec)).detach().numpy()
            best_move = None
            for idx in np.argsort(q_vals)[::-1]:
                if idx in legal_indices:
                    best_move = decode_action(idx)
                    break

            if best_move:
                pygame.time.delay(500)  # Slow down AI move a bit
                game.make_move(current_player, best_move)

        # Check win
        alive = [p for p in game.players if p.active]
        if len(alive) == 1:
            print(f"{alive[0].name} wins!")
            pygame.time.delay(2000)
            running = False

        game.next_player()
        current_player = game.players[game.current_index]
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    play_human_vs_ai()