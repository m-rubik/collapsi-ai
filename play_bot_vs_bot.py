"""
CSB = Collapsi Solver Bot
"""

import random
from collapsi.configs.configs import *
from collapsi.modules.game import *
from collapsi.utilities.solver import *
from collapsi.utilities.vprint import vprint

# --------------------------
# Play two CSBs against each other
# --------------------------
if __name__ == "__main__":
    csb1_wins = 0
    csb2_wins = 0
    for i in range(10):
        print("Running game", i)
        game = GameState(num_players=2)
        game.players[0].name = 'P1'
        game.players[1].name = 'P2'

        vprint("Initial board:")
        if PRINT_VERBOSE:
            game.print_board()

        while not game.is_terminal:
            # ---- CSB1 turn ----
            vprint("CSB1 possible moves:", game.get_current_player_moves())
            vprint("CSB1 is thinking...")
            s = Solver(game)
            win, moves = s.best_moves(game)
            if win:
                if isinstance(moves, list):
                    move = random.choice(moves)
                else:
                    move = moves
                vprint("After considering {} possible game states, CSB1 thinks it can win with move: {}".format(len(s.memoized_states.keys()), move))
            else:
                move = random.choice(game.get_current_player_moves())
                vprint("After considering {} possible game states, CSB1 thinks it cannot win, so it takes a random move: {}".format(len(s.memoized_states.keys()), move))

            game.make_move(game.current_player, move)
            game.next_player()
            if PRINT_VERBOSE:
                game.print_board()
            if game.is_terminal:
                print("Game over! CSB1 wins!")
                csb1_wins += 1
                break

            # ---- CSB2 turn ----
            vprint("CSB2 possible moves:", game.get_current_player_moves())
            vprint("CSB2 is thinking...")
            s = Solver(game)
            win, moves = s.best_moves(game)
            if win:
                if isinstance(moves, list):
                    move = random.choice(moves)
                else:
                    move = moves
                vprint("After considering {} possible game states, CSB2 thinks it can win with move: {}".format(len(s.memoized_states.keys()), move))
            else:
                move = random.choice(game.get_current_player_moves())
                vprint("After considering {} possible game states, CSB2 thinks it cannot win, so it takes a random move: {}".format(len(s.memoized_states.keys()), move))

            game.make_move(game.current_player, move)
            game.next_player()
            if PRINT_VERBOSE:
                game.print_board()

            memo = {}
            if game.is_terminal:
                print("Game over! CSB2 wins!")
                csb2_wins += 1
                break

        print("CSB1 WINS: {}, CSB2 WINS: {}".format(csb1_wins, csb2_wins))