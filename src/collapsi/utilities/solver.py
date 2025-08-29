from copy import deepcopy
from collapsi.configs.configs import *
from collapsi.modules.agent import *
from collapsi.modules.game import *
from collapsi.utilities.vprint import vprint

class Solver():
    def __init__(self, game_state):
        self.game_state = game_state
        self.memoized_states = {}

    def canonical(self, game_state):
        """Return a hashable representation of the game state."""
        board_tuple = tuple(
            tuple((card.value, card.collapsed) for card in row) for row in game_state.board
        )
        positions = tuple((p.position for p in game_state.players))
        return (board_tuple, game_state.current_index, positions)
        # return (tuple(map(tuple, game_state.board)), game_state.current_player.name)

    def solve(self, game_state):
        key = self.canonical(game_state)
        if key in self.memoized_states:
            return self.memoized_states[key]

        if game_state.is_terminal:
            self.memoized_states[key] = (False, None)  # current player loses
            return False

        for move in sorted(game_state.get_current_player_moves()):
            # Work on a copy
            new_game_state = deepcopy(game_state)
            new_game_state.make_move(new_game_state.current_player, move)
            new_game_state.next_player()
            if not self.solve(new_game_state):  # opponent loses ⇒ current wins
                self.memoized_states[key] = (True, move)  # winning, store this move
                return True
                
        self.memoized_states[key] = (False, None)
        # print(len(memoized_states.keys()))
        return False

    def best_moves(self, game_state):
        """
        Returns (is_winning, list_of_winning_moves)
        If losing, the list is empty.
        """
        self.solve(game_state)  # ensures memo is populated
        key = self.canonical(game_state)
        return self.memoized_states[key]

if __name__ == "__main__":
    game_state = GameState(num_players=2)
    game_state.players[0].name = 'P1'
    game_state.players[1].name = 'P2'

    # Use a fixed set of positions
    # game.board = [[Card("3"), Card("Joker"), Card("Joker"), Card("A")],
    #               [Card("A"), Card("4"), Card("A"), Card("3")],
    #               [Card("2"), Card("2"), Card("2"), Card("2")],
    #               [Card("4"), Card("3"), Card("3"), Card("A")]]
    
    # game_state.board = [[Card("3", True), Card("Joker", True), Card("Joker", True), Card("2", True)],
    #               [Card("4", True), Card("A"), Card("A"), Card("3", True)],
    #               [Card("2", True), Card("2"), Card("A"), Card("2", True)],
    #               [Card("4", True), Card("3", True), Card("3", True), Card("A", True)]]
    # game_state.players[0].position=(1,1)
    # game_state.players[1].position=(2,2)
    # game_state.current_index = 1

    # THIS IS A LOSING STATE FOR P1, RIGHT OFF THE RIP
    # game_state.board = [[Card("2"), Card("Joker"), Card("4"), Card("3")],
    #                     [Card("A"), Card("A"), Card("A"), Card("2")],
    #                     [Card("3"), Card("Joker"), Card("3"), Card("A")],
    #                     [Card("4"), Card("2"), Card("2"), Card("3")]]
    # game_state.players[0].position=(0,1)
    # game_state.players[1].position=(2,1)
    # game_state.current_index = 0

    # game_state.board = [[Card("A", True), Card("2", True), Card("3"), Card("Joker", True)],
    #                     [Card("A"), Card("A", True), Card("2"), Card("4")],
    #                     [Card("4"), Card("3", True), Card("3"), Card("2")],
    #                     [Card("A"), Card("2", True), Card("3"), Card("Joker", True)]]
    # game_state.players[0].position=(3,0)
    # game_state.players[1].position=(1,0)
    # game_state.current_index = 1

    # game_state.board = [[Card("Joker", True), Card("3", True), Card("A", True), Card("Joker", True)],
    #                     [Card("A", True), Card("A", True), Card("3", True), Card("3", True)],
    #                     [Card("2"), Card("2"), Card("4"), Card("2")],
    #                     [Card("3"), Card("2", True), Card("A"), Card("4")]]
    # game_state.players[0].position=(2,0)
    # game_state.players[1].position=(3,0)
    # game_state.current_index = 1

    # Jx  2x  P2  Ax
    # P1  Ax  3x  3x
    # A   4x  4   Jx
    # 2   2x  Ax  3
    game_state.board = [[Card("Joker", True), Card("2", True), Card("3"), Card("A", True)],
                        [Card("2"), Card("A", True), Card("3", True), Card("3", True)],
                        [Card("A"), Card("4", True), Card("4"), Card("Joker", True)],
                        [Card("2"), Card("2", True), Card("A"), Card("3")]]
    game_state.players[0].position=(1,0)
    game_state.players[1].position=(3,2)
    game_state.current_index = 1

    print("\nSolving the following board...")

    game_state.print_board()

    print("Where it is {}'s turn".format(game_state.current_player.name))
    
    print("P2 moves:", game_state.get_current_player_moves())

    # Run solver once from starting state
    s = Solver(game_state)
    win, moves = s.best_moves(game_state)

    print("Searched {} states to find solution".format(len(s.memoized_states.keys())))
    
    if win:
        print(f"This state is WINNING for {s.game_state.current_player.name}")
        print("Computed winning move is:", moves)
    else:
        print(f"This state is LOSING for {s.game_state.current_player.name}")
