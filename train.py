import random
import torch
from collapsi.configs.configs import *
from collapsi.modules.agent import *
from collapsi.modules.game import *
from collapsi.utilities.vprint import vprint

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
