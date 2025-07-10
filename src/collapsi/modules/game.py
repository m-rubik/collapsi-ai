import random
from copy import deepcopy
from collapsi.configs.configs import *
from collapsi.modules.card import Card
from collapsi.modules.player import Player
from collapsi.utilities.vprint import vprint

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