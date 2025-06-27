import random
import torch
from copy import deepcopy
from collapsi.configs.configs import *
from collapsi.modules.card import Card
from collapsi.modules.agent import *
from collapsi.utilities.vprint import vprint

class Player:
    def __init__(self, name, position):
        self.name = name
        self.position = position
        self.active = True

class GameState:
    def __init__(self, num_players=2):
        assert num_players <= 2, "Currently only 2 jokers exist in the deck"
        self.board = self.create_board()
        self.players = self.init_players(num_players)
        self.current_index = 0  # whose turn it is

    def create_board(self):
        cards = deepcopy(CARD_VALUES)
        random.shuffle(cards)
        return [[Card(cards.pop()) for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

    def init_players(self, num_players):
        jokers = []
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c].value == 'Joker':
                    jokers.append((r, c))
        players = []
        for i in range(num_players):
            players.append(Player(name=f"P{i+1}", position=jokers[i]))
        return players

    def print_board(self):
        board_copy = [[self.board[r][c].__repr__() for c in range(BOARD_SIZE)] for r in range(BOARD_SIZE)]
        for player in self.players:
            if player.active:
                r, c = player.position
                board_copy[r][c] = player.name + ' '
        for row in board_copy:
            vprint(" ".join(row))

    def get_player_moves(self, player):
        r, c = player.position
        card = self.board[r][c]
        vprint(f"Player is on tile {card}")

        if card.collapsed:
            return []

        steps_options = CARD_NUMERIC[card.value]
        if not isinstance(steps_options, list):
            steps_options = [steps_options]

        other_positions = {p.position for p in self.players if p != player and p.active}
        moves = set()

        def dfs(path, steps_remaining):
            if steps_remaining == 0:
                final = path[-1]
                if final != (r, c) and final not in other_positions:
                    moves.add(final)
                return
            for dr, dc in DIRECTIONS:
                nr, nc = (path[-1][0] + dr) % BOARD_SIZE, (path[-1][1] + dc) % BOARD_SIZE
                if self.board[nr][nc].collapsed or (nr, nc) in path:
                    continue
                dfs(path + [(nr, nc)], steps_remaining - 1)

        for steps in steps_options:
            dfs([(r, c)], steps)

        return list(moves)

    def make_move(self, player, destination):
        r, c = player.position
        self.board[r][c].collapsed = True
        player.position = destination

    def next_player(self):
        # rotate to next active player
        for _ in range(len(self.players)):
            self.current_index = (self.current_index + 1) % len(self.players)
            if self.players[self.current_index].active:
                return

    def play_turn(self):
        player = self.players[self.current_index]
        if not player.active:
            self.next_player()
            return True

        moves = self.get_player_moves(player)
        if not moves:
            vprint(f"{player.name} is stuck and eliminated.")
            player.active = False
            active_players = [p for p in self.players if p.active]
            if len(active_players) == 1:
                vprint(f"{active_players[0].name} wins!")
                return False
            self.next_player()
            return True

        move = random.choice(moves)
        self.make_move(player, move)
        self.next_player()
        return True

    def play_game(self):
        while True:
            self.print_board()
            if not self.play_turn():
                break

    def encode_state(self):
        # Useful for the agent to track Q-values
        return self  # The agent already has encode_state() to handle this

    def reset(self):
        # Full game restart
        self.__init__(num_players=len(self.players))
        return self

def train_dqn_agent(agent, episodes=1000):
    wins = 0
    win_counter = []

    for episode in range(1, episodes+1):
        game = GameState(num_players=2)
        game.players[0].name = 'P1'  # The agent
        game.players[1].name = 'P2'  # Random player

        done = False
        current_player_idx = 0

        # Because we give reward based on previous turn
        previous_state_vec_start_of_turn = encode_state(game, agent_name='P1')
        previous_state_vec_end_of_turn = encode_state(game, agent_name='P1')
        previous_action_idx = 0
        previous_len_enemy_legal_moves = len(game.get_player_moves(game.players[1]))

        while not done:
            current_player = game.players[current_player_idx]

            vprint(f"Start of round for {current_player.name}...")
            if PRINT_VERBOSE:
                game.print_board()

            # Agent turn
            # When the agent takes its turn, we don't want to reward it (agent.remember) until the next player takes their turn
            # Why?
            # Let's say the agent moves and it gets a reward for surviving another turn.
            # Then the next player moves
            # Then on the agent's turn, it doesn't have any moves! Agent just lost.
            # But we can't punish it for doing nothing (that violates how q learning works, it has to go from state A --> action --> state B and get a reward)
            # So what we actually have to do is punish it for it's PREVIOUS move that led to it losing
            if current_player.name == 'P1' and current_player.active:
                state_vec_start_of_turn = encode_state(game, agent_name='P1')
                legal_moves = game.get_player_moves(current_player)
                vprint(legal_moves)

                # If it does not have any legal moves, it loses!
                if not legal_moves:
                    current_player.active = False
                    vprint("Game over. Winner: P2")
                    agent.remember(previous_state_vec_start_of_turn, previous_action_idx, AGENT_REWARDS['LOSS'], previous_state_vec_end_of_turn, True)
                    agent.update_model()
                    done = True
                    win_counter.append(wins)
                    break

                legal_action_indices = [encode_action(r, c) for (r, c) in legal_moves]
                q_vals = agent.model(torch.tensor(state_vec_start_of_turn, dtype=torch.float32)).detach().numpy()

                # Sort all actions by Q-value (descending)
                sorted_actions = np.argsort(q_vals)[::-1]

                # Take the highest-ranked legal action
                action_idx = None
                for a in sorted_actions:
                    if a in legal_action_indices:
                        action_idx = a
                        break

                # Fallback if none found
                if action_idx is None:
                    action_idx = random.choice(legal_action_indices)

                move = decode_action(action_idx)
                game.make_move(current_player, move)

                previous_state_vec_start_of_turn = state_vec_start_of_turn
                previous_state_vec_end_of_turn = encode_state(game, agent_name='P1')
                previous_action_idx = action_idx

            # Enemy (Random) player who always takes random action!
            elif current_player.name == 'P2' and current_player.active:
                legal_moves = game.get_player_moves(current_player)
                vprint(legal_moves)
                if legal_moves:
                    game.make_move(current_player, random.choice(legal_moves))
                else:
                    current_player.active = False

            # End condition
            alive = [p for p in game.players if p.active]
            if len(alive) == 1:
                done = True
                winner = alive[0].name
                final_reward = AGENT_REWARDS["WIN"] if winner == 'P1' else AGENT_REWARDS["LOSS"]
                vprint(f"Game over. Winner: {winner}")
                agent.remember(previous_state_vec_start_of_turn, previous_action_idx, final_reward, previous_state_vec_end_of_turn, True)
                agent.update_model()
                if winner == 'P1':
                    wins += 1
                win_counter.append(wins)
            elif current_player.name == 'P2':
                scale = 1
                if len(legal_moves) < previous_len_enemy_legal_moves:
                    scale = 1+abs(len(legal_moves)-previous_len_enemy_legal_moves)
                vprint(f"Game continuing... surviving scale: {scale}")
                agent.remember(previous_state_vec_start_of_turn, previous_action_idx, scale*AGENT_REWARDS['SURVIVE_ANOTHER_ROUND'], previous_state_vec_end_of_turn, False)
                agent.update_model()
                previous_len_enemy_legal_moves = len(legal_moves)
            else:
                pass
                

            # Next turn
            game.next_player()
            current_player_idx = game.current_index

        if episode % 1000 == 0:
            print(f"Episode {episode}: Win rate = {wins/episode}, Epsilon = {agent.epsilon:.3f}")


    print(f"Final win rate: {wins}/{episodes}")
    return win_counter


agent = DQNAgent(state_dim=36, action_dim=16) # 16 possible tile moves on 4x4

if LOAD_DQN_MODEL:
    agent.model.load_state_dict(torch.load(DQN_MODEL_NAME))

win_counter = train_dqn_agent(agent=agent, episodes=NUM_ROUNDS)

if SAVE_DQN_MODEL:
    torch.save(agent.model.state_dict(), DQN_MODEL_NAME)

import numpy as np
if not PRINT_VERBOSE:
    # PLOT STUFF
    import matplotlib.pyplot as plt

    x = [i for i in range(NUM_ROUNDS)]

    x_np = np.array(x)
    y_np = np.array(win_counter)

    plt.plot(x, win_counter, label="Wins", marker='o')  # Wins

    # Perform linear fit (forcing intercept to 0)
    slope, _ = np.polyfit(x_np, y_np, 1, full=False)  # Fit without intercept
    trendline = slope * x_np  # Use slope and force intercept to 0

    # Plot trendline
    plt.plot(x, trendline, label="Trendline", color="red", linestyle="--")

    # Add text with the slope value
    plt.text(x[0], trendline[0], f"Slope: {slope:.2f}", fontsize=12, color="red", verticalalignment="top")

    plt.xlabel("Episode")
    plt.ylabel("Count")
    plt.title("Total Win Count v.s Episode Number")
    plt.legend()  # Show legend
    plt.grid(True)  # Add grid for better visibility
    plt.show()