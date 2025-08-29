import random
from collapsi.configs.configs import *
from collapsi.modules.game import *
from collapsi.utilities.solver import *
from collapsi.utilities.vprint import vprint

# --------------------------
# Interactive play
# --------------------------
if __name__ == "__main__":
    random_wins = 0
    bot_wins = 0
    for i in range(10):
        print("Playing game", i)
        game = GameState(num_players=2)
        game.players[0].name = 'P1'
        game.players[1].name = 'P2'

        vprint("Initial board:")
        if PRINT_VERBOSE:
            game.print_board()

        while not game.is_terminal:
            # ---- Human move ----
            vprint("Your move options:", game.get_current_player_moves())

            move = input("Enter your move: ")  # You may need to adapt input format
            move = eval(move)  # if moves are tuples, e.g., (row, col)

            # TAKE A RANDOM MOVE
            # move = random.choice(game.get_current_player_moves())

            game.make_move(game.current_player, move)
            game.next_player()
            if PRINT_VERBOSE:
                game.print_board()
            if game.is_terminal:
                vprint("Game over! Human wins!")
                random_wins += 1
                break

            # ---- Bot move ----
            vprint("Bot's possible moves:", game.get_current_player_moves())
            vprint("Bot is thinking...")
            s = Solver(game)
            win, moves = s.best_moves(game)
            if win:
                if isinstance(moves, list):
                    bot_move = random.choice(moves)
                else:
                    bot_move = moves
                vprint("After considering {} possible game states, Bot thinks it can win with move: {}".format(len(s.memoized_states.keys()), bot_move))
            else:
                bot_move = random.choice(game.get_current_player_moves())
                vprint("After considering {} possible game states, Bot thinks it cannot win, so it takes a random move: {}".format(len(s.memoized_states.keys()), bot_move))

            game.make_move(game.current_player, bot_move)
            game.next_player()
            if PRINT_VERBOSE:
                game.print_board()

            memo = {}
            if game.is_terminal:
                vprint("Game over! Bot wins!")
                bot_wins += 1
                break

    print("RANDOM-BOT WINS: {}, SOLVER-BOT WINS: {}".format(random_wins, bot_wins))