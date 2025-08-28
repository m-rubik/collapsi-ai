CARD_VALUES = ['Joker', 'Joker'] + ['A'] * 4 + ['2'] * 4 + ['3'] * 4 + ['4'] * 2
CARD_NUMERIC = {'A': 1, '2': 2, '3': 3, '4': 4, 'Joker': [1, 2, 3, 4]}
CARD_TO_NUM = {
    'A': 1,
    '2': 2,
    '3': 3,
    '4': 4,
    'Joker': 0  # or 5 if you want it distinct
}
CARD_TO_NUM_NORMALIZED = {
    'A': -0.5,
    '2': 0,
    '3': 0.5,
    '4': 1,
    'Joker': 0  # or ?? if you want it distinct
}

BOARD_SIZE = 4
DIRECTIONS = [(-1,0), (1,0), (0,-1), (0,1)]  # up, down, left, right

NUMBER_OF_PLAYERS = 2

PRINT_VERBOSE = False
NUM_ROUNDS = 50000
LOAD_DQN_MODEL = False
SAVE_DQN_MODEL = True
DQN_MODEL_NAME = "collapsi_model.pth"
AGENT_EXPLORING = True

AGENT_REWARDS = {
    "LOSS": -10.0,
    "SURVIVE_ANOTHER_ROUND": 1,
    "WIN": 20.0,
}