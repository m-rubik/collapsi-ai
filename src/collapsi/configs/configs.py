CARD_VALUES = ['Joker', 'Joker'] + ['A'] * 4 + ['2'] * 4 + ['3'] * 4 + ['4'] * 2
CARD_NUMERIC = {'A': 1, '2': 2, '3': 3, '4': 4, 'Joker': [1, 2, 3, 4]}

BOARD_SIZE = 4
DIRECTIONS = [(-1,0), (1,0), (0,-1), (0,1)]  # up, down, left, right

NUMBER_OF_PLAYERS = 2

PRINT_VERBOSE = False
NUM_ROUNDS = 100000
LOAD_QTABLE = False
SAVE_QTABLE = True
QTABLE_NAME = "qtable.pkl"
AGENT_EXPLORING = True

# # Game modifiers
# MAX_TURNS = 200
# AGENT_COUNT = 1
# AGENT_ACTIONS_PER_TURN = 4
# FLOOR_COUNT = 1
# STEALTH_TOKENS = 3
# GRID_SIZE = 4 # The grid is a square GRID_SIZE x GRID_SIZE
# USE_WALLS = True # Controls whether or not to place walls
# FIXED_WALLS = False # Controls whether to use a fixed wall layout, or randomized

# ### NOTE/TODO: 
# # - These values do not account for walls
# # - These values do not account for tiles that inhibit/impair motion
# # - These values do not account for guard positioning/movement
# # - These values do not account for other other agent's positioning/movement
# WORST_CASE_ACTIONS_TO_FIND_SAFE = (GRID_SIZE**2)-1 # Worst case, it would take (GRID_SIZE^2)-1 actions to find the safe (agent tries every other tile and safe is on the last one)
# WORST_CASE_ACTIONS_TO_ESCAPE = (GRID_SIZE-1)*2 # Worst case, it takes (GRID_SIZE-1)*2 actions to return to (safe is at opposite corner as exit)
# ###

# ### NOTE/TODO:
# # - This value does not account for the "real" safe cracking mechanism
# BEST_CASE_ACTIONS_TO_CRACK_SAFE = 1

# PUNISHMENT_FOR_MOVING = -1 # The base "reward" for moving must be a slight punishment, else we risk the agent just moving around arbitrarily to gain rewards
# PUNISHMENT_FOR_LOSING = -1000 # Huge penalty for losing
# PUNISHMENT_FOR_BAD_SAFE_CRACK_ACTION_USE = -75  # Punish for trying to crack a safe when not standing on a safe, or for trying to crack a safe that is already cracked
# PUNISHMENT_FOR_ILLEGAL_MOVE_ACTION = -100  # Punish for trying to take an illegal move action

# REWARD_FOR_FINDING_SAFE = 25 # Small reward for finding the safe
# REWARD_FOR_SAFE_CRACK_ATTEMPT = 50 # Small reward for attempting to crack the safe while standing on it
# REWARD_FOR_CRACKING_SAFE = 100 # Medium reward for cracking the safe
# REWARD_FOR_WINNING = 1000 # Huge reward for winning

# # To determine the maximum punishment for losing stealth, we must consider the worst-case scenario, wherein the agent, through bad luck, uses:
# # WORST_CASE_ACTIONS_TO_FIND_SAFE and WORST_CASE_ACTIONS_TO_ESCAPE
# # Now, with respect to reward/punishment, the "worst" case scenario is actually cracking the safe on the first attempt, because each attempt rewards the agent. 
# # We must also consider how much the agent is rewarded for winning.
# # We must ensure that if the agent is unlucky, it still receives a net reward for escaping, even if it loses all stealth.
# # This allows the agent to learn that it's not necessarily a terrible thing to lose stealth, and stealth can be sacrificed for strategic purposes.
# DESIRED_REWARD_IN_WORST_CASE = 10
# PUNISHMENT_FOR_LOSING_STEALTH = -1 * (((WORST_CASE_ACTIONS_TO_FIND_SAFE+WORST_CASE_ACTIONS_TO_ESCAPE)*PUNISHMENT_FOR_MOVING + REWARD_FOR_FINDING_SAFE + REWARD_FOR_CRACKING_SAFE + REWARD_FOR_SAFE_CRACK_ATTEMPT + REWARD_FOR_WINNING) - DESIRED_REWARD_IN_WORST_CASE) / STEALTH_TOKENS