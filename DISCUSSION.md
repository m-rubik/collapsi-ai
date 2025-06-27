## Findings
Tabular Q-learning (using Q-Tables) struggles when the state spaces is large.

If you treat the agent like you would treat a human playing the game, as in, you make
the state contain all the information a human would have, the possible number of unique states is **huge**!

At first, I didn't realize this, and so I wrote the state that was given to the agent to contain:
- The value of each card in the grid + whether it was collapsed or not
- The position of each player

But considering the amount of different possibilities for each card's value + collapsed status + player position, the total number of possible states in **massive**, far beyond what is practical for how many cycles I want to run.


Tabular q-learning works by encountering the same state(s) over
and over and learning what to do in each state. It is "discrete", which is to say, it treats every unique state as totally unrelated

So, to get better results, we need to either:
1) Reduce the number of possible states by simplifying what goes into the state, or
2) Change away from tabular q-learning to a new approach that isn't discrete (Deep Q-Learning)

### APPROACH 1: Reduce state space
Instead of tracking every card value, what if we just tracked whether each card is collapsed or not?

If the board is 4×4 = 16 cards, and each card can be collapsed (True) or not (False), then:

Total collapsed card combinations = 2^16 = 65,536

But then, with 2 players. Players can be on any of the 16 tiles except collapsed ones

For worst-case estimation, ignore that constraint (i.e., estimate the max possible)

So, both players have 16 possible positions, but they can't be in the same position concurrently, so subtract invalid ones

Total player position pairs: 16 × 15 = 240

Therefore, total state space = collapsed_combinations × player_position_pairs
= 65,536 × 240
= 15,728,640

So **~16 million possible unique states** in this encoding.

BUT: In real games:
- Many states are unreachable (e.g., both players on collapsed tiles)
- Many states are repeated (e.g., early-game setups)

So the effective state space is likely less, but let's assume worst-case.