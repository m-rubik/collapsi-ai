"""
CSB = Collapsi Solver Bot
"""

import random
from collapsi.configs.configs import *
from collapsi.modules.game import *
from collapsi.utilities.solver import *
from collapsi.utilities.vprint import vprint

# --------------------------
# Play random bot against CSB
# --------------------------
if __name__ == "__main__":
    random_bot_wins = 0
    csb_wins = 0
    for i in range(1000):
        print("Running game", i)
        game = GameState(num_players=2)
        game.players[0].name = 'P1'
        game.players[1].name = 'P2'

        vprint("Initial board:")
        if PRINT_VERBOSE:
            game.print_board()

        while not game.is_terminal:
            # ---- Random Bot turn ----
            vprint("Random Bot possible moves:", game.get_current_player_moves())
            move = random.choice(game.get_current_player_moves())
            vprint("Random Bot takes move: {}".format(move))

            game.make_move(game.current_player, move)
            game.next_player()
            if PRINT_VERBOSE:
                game.print_board()
            if game.is_terminal:
                print("Game over! Random Bot wins!")
                random_bot_wins += 1
                break

            # ---- CSB turn ----
            vprint("CSB possible moves:", game.get_current_player_moves())
            vprint("CSB is thinking...")
            s = Solver(game)
            win, moves = s.best_moves(game)
            if win:
                if isinstance(moves, list):
                    move = random.choice(moves)
                else:
                    move = moves
                vprint("After considering {} possible game states, CSB thinks it can win with move: {}".format(len(s.memoized_states.keys()), move))
            else:
                move = random.choice(game.get_current_player_moves())
                vprint("After considering {} possible game states, CSB thinks it cannot win, so it takes a random move: {}".format(len(s.memoized_states.keys()), move))

            game.make_move(game.current_player, move)
            game.next_player()
            if PRINT_VERBOSE:
                game.print_board()

            memo = {}
            if game.is_terminal:
                print("Game over! CSB wins!")
                csb_wins += 1
                break

        print("Random Bot WINS: {}, CSB WINS: {}".format(random_bot_wins, csb_wins))