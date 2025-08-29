from copy import deepcopy
from collapsi.configs.configs import *
from collapsi.modules.agent import *
from collapsi.modules.game import *
from collapsi.utilities.vprint import vprint

class Solver():
    def __init__(self, game_state):
        self.game_state = game_state
        self.memoized_states = {}
        pass

    def canonical(self, game_state):
        """Return a hashable representation of the game state."""
        # Example: encode board + current player
        return (tuple(map(tuple, game_state.board)), game_state.current_player.name)

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

    print("\nSolving the following board...")

    game_state.print_board()

    print("Where it is {}'s turn".format(game_state.current_player.name))
    
    # Run solver once from starting state
    s = Solver(game_state)
    win, moves = s.best_moves(game_state)

    print("Searched {} states to find solution".format(len(s.memoized_states.keys())))
    
    if win:
        print(f"This state is WINNING for {s.game_state.current_player.name}")
        print("Computed winning move is:", moves[0])
    else:
        print(f"This state is LOSING for {s.game_state.current_player.name}")
