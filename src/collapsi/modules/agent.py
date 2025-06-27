"""
"""

import random
import pickle
import numpy as np
from collections import defaultdict
from collapsi.configs.configs import *
from collapsi.utilities.vprint import vprint

# Q-learning constants
if AGENT_EXPLORING:  
    epsilon = 0.2  # Exploration rate
else:
    epsilon = 0  # Do not explore
alpha = 0.02  # Learning rate
gamma = 0.9  # Discount factor

if LOAD_QTABLE:
    with open(QTABLE_NAME, 'rb') as file:
        Q_TABLE = pickle.load(file)
else:
    Q_TABLE = {}

class Agent:
    def __init__(self, name):
        self.name = name
        self.q_table = Q_TABLE
        self.current_state = None
        self.current_action = None
        self.current_legal_actions = None

    def get_state_key(self, state):

        # TODO: Can I reduce the size of this state space further while still allowing the agent to have a meaningful state to learn from?

        # This is a true representation of the grid, but...
        # this is in the order of 10^9 states. Way too many!
        # board_state = tuple((card.value, card.collapsed) for row in state.board for card in row)

        # This is a representation of the grid only with a true/false if the tile is collapsed, but...
        # this is in the order of ~15 million states, still a lot!
        board_state  = tuple(tuple(card.collapsed for card in row) for row in state.board)

        player_positions = tuple(p.position for p in state.players)
        return (board_state, player_positions)

    def select_action(self, state, legal_moves):
        state_key = self.get_state_key(state)

        best_value = float('-inf')
        best_actions = []
        for move in legal_moves:
            q = self.q_table.get((state_key, move), 0.0)
            if q > best_value:
                best_value = q
                best_actions = [move]
            elif q == best_value:
                best_actions.append(move)

        if random.random() < epsilon:
            action = random.choice(legal_moves)
        else:
            action = random.choice(best_actions)

        self.current_action = action
        self.current_state = state_key  # ← store only state key, not full (state, action)
        return action
    
    def save_current_state(self, state):
        self.current_state = self.get_state_key(state)

    def update_q_table(self, reward, new_state, possible_actions):
        new_state_key = self.get_state_key(new_state)

        # Estimate best future reward
        if possible_actions:
            best_next_q = max(
                self.q_table.get((new_state_key, a), 0.0) for a in possible_actions
            )
        else:
            best_next_q = 0.0

        # Update Q-value
        key = (self.current_state, self.current_action)
        current_q = self.q_table.get(key, 0.0)
        self.q_table[key] = (1 - alpha) * current_q + alpha * (reward + gamma * best_next_q)

        vprint(f"Updated Q[{key}] = {self.q_table[key]:.4f}")
    
# DQN agent for Collapsi

import torch
import torch.nn as nn
import torch.optim as optim
import random
import numpy as np
from collections import deque

# --- Neural Network for Q(s) -> Q(a) ---
class DQN(nn.Module):
    def __init__(self, state_dim, action_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, action_dim)
        )

    def forward(self, x):
        return self.net(x)

# --- DQN Agent ---
class DQNAgent:
    def __init__(self, state_dim=20, action_dim=16, gamma=0.99, epsilon=1.0, epsilon_min=0.05, epsilon_decay=0.99999, lr=1e-3):
        self.model = DQN(state_dim, action_dim)
        self.target_model = DQN(state_dim, action_dim)
        self.target_model.load_state_dict(self.model.state_dict())
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)
        self.criterion = nn.MSELoss()
        self.buffer = deque(maxlen=100_000)
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.action_dim = action_dim
        self.steps = 0

    def select_action(self, state_vec):
        if random.random() < self.epsilon:
            return random.randint(0, self.action_dim - 1)
        with torch.no_grad():
            q_vals = self.model(torch.tensor(state_vec, dtype=torch.float32))
            return torch.argmax(q_vals).item()

    def remember(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))

    def update_model(self, batch_size=32):
        if len(self.buffer) < batch_size:
            return

        batch = random.sample(self.buffer, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)

        states = torch.tensor(states, dtype=torch.float32)
        actions = torch.tensor(actions).unsqueeze(1)
        rewards = torch.tensor(rewards, dtype=torch.float32)
        next_states = torch.tensor(next_states, dtype=torch.float32)
        dones = torch.tensor(dones, dtype=torch.float32)

        q_values = self.model(states).gather(1, actions).squeeze(1)
        next_q = self.target_model(next_states).max(1)[0]
        target_q = rewards + self.gamma * next_q * (1 - dones)

        loss = self.criterion(q_values, target_q.detach())
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # Epsilon decay
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

        # Soft update (optional): every N steps, update target network
        self.steps += 1
        if self.steps % 100 == 0:
            self.target_model.load_state_dict(self.model.state_dict())

# --- Utility to encode the game state into a vector ---
def encode_state(state, agent_name):
    board = state.board
    collapsed = [1.0 if card.collapsed else 0.0 for row in board for card in row]
    
    agent_pos = None
    enemy_pos = None
    for p in state.players:
        if p.name == agent_name:
            agent_pos = p.position
        else:
            enemy_pos = p.position

    # Normalize positions to [0, 1]
    agent_vec = [agent_pos[0] / 4.0, agent_pos[1] / 4.0]
    enemy_vec = [enemy_pos[0] / 4.0, enemy_pos[1] / 4.0]

    return np.array(collapsed + agent_vec + enemy_vec, dtype=np.float32)  # length 20

# --- Utility to decode action index to (row, col) ---
def decode_action(index):
    return (index // 4, index % 4)

# --- Utility to encode (row, col) to action index ---
def encode_action(row, col):
    return row * 4 + col