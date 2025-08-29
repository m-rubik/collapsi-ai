import random
from collapsi.configs.configs import *
from collapsi.modules.game import *
from collapsi.utilities.solver import *
from collapsi.utilities.vprint import vprint

# --------------------------
# Interactive play human vs bot
# --------------------------
if __name__ == "__main__":
    game = GameState(num_players=2)
    game.players[0].name = 'P1'
    game.players[1].name = 'P2'

    vprint("Initial board:")
    if PRINT_VERBOSE:
        game.print_board()

    while not game.is_terminal:
        # ---- Human move ----
        print("Your move options:", game.get_current_player_moves())

        move = input("Enter your move: ")  # You may need to adapt input format
        move = eval(move)  # if moves are tuples, e.g., (row, col)

        # TAKE A RANDOM MOVE
        # move = random.choice(game.get_current_player_moves())

        game.make_move(game.current_player, move)
        game.next_player()
        game.print_board()
        if game.is_terminal:
            print("Game over! You win!")
            break

        # ---- Bot move ----
        print("Bot's possible moves:", game.get_current_player_moves())
        print("Bot is thinking...")
        s = Solver(game)
        win, moves = s.best_moves(game)
        if win:
            if isinstance(moves, list):
                bot_move = random.choice(moves)
            else:
                bot_move = moves
            print("After considering {} possible game states, Bot thinks it can win with move: {}".format(len(s.memoized_states.keys()), bot_move))
        else:
            bot_move = random.choice(game.get_current_player_moves())
            print("After considering {} possible game states, Bot thinks it cannot win, so it takes a random move: {}".format(len(s.memoized_states.keys()), bot_move))

        game.make_move(game.current_player, bot_move)
        game.next_player()
        game.print_board()

        memo = {}
        if game.is_terminal:
            print("Game over! Bot wins!")
            break