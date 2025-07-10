"""
"""


import torch
import torch.nn as nn
import torch.optim as optim
import random
import numpy as np
from collections import deque
from collapsi.configs.configs import *
from collapsi.utilities.vprint import vprint

# Q-learning constants
if AGENT_EXPLORING:  
    epsilon = 1.0  # Exploration rate
    epsilon_min = 0.05 # Min exploration rate
else:
    # Do not explore
    epsilon = 0
    epsilon_min = 0

epsilon_decay=0.999999 # Decay in exploration rate
gamma = 0.95  # Discount factor
lr=1e-3 # Learning rate

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
    def __init__(self, state_dim=36, action_dim=16, gamma=gamma, epsilon=epsilon, epsilon_min=epsilon_min, epsilon_decay=epsilon_decay, lr=lr):
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
    # Encode board: each tile = [card_value, collapsed_flag]
    flat_board = []
    for row in state.board:
        for card in row:
            # card_val = CARD_NUMERIC[card.value]
            # collapsed = 1.0 if card.collapsed else 0.0
            # flat_board.extend([card_val / 4.0, collapsed])  # Normalize card value
            card_val = CARD_TO_NUM_NORMALIZED[card.value]
            collapsed = 0.5 if card.collapsed else -0.5 # Centered around 0 for activation functions
            flat_board.extend([card_val, collapsed])

    # Encode player positions
    agent_pos = None
    enemy_pos = None
    for p in state.players:
        if p.name == agent_name:
            agent_pos = p.position
        else:
            enemy_pos = p.position

    # agent_vec = [agent_pos[0] / 4.0, agent_pos[1] / 4.0]
    # enemy_vec = [enemy_pos[0] / 4.0, enemy_pos[1] / 4.0]

    # Position: center from [0,4] --> [-0.5, 0.5]
    agent_vec = [(agent_pos[0]-2) / 4.0, (agent_pos[1]-2) / 4.0]
    enemy_vec = [(enemy_pos[0]-2) / 4.0, (enemy_pos[1]-2) / 4.0]

    return np.array(flat_board + agent_vec + enemy_vec, dtype=np.float32) # 36 dimension

# --- Utility to decode action index to (row, col) ---
def decode_action(index):
    return (index // 4, index % 4)

# --- Utility to encode (row, col) to action index ---
def encode_action(row, col):
    return row * 4 + col