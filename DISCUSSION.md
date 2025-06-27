## Initial Approach
My initial approach was as follows
1. Simulate the game
2. Add a simple tabular Q-learning agent to play the game against a bot that only takes random moves
3. Train the agent to learn to play and consistently beat the "random" opponent

## Findings
Tabular Q-learning (using Q-Tables) struggles when the state spaces is large.

If you treat the agent like you would treat a human playing the game, as in, you make
the state contain all the information a human would have, the possible number of unique states is **huge**!

At first, I didn't realize this, and so I wrote the state that was given to the agent to contain:
- The value of each card in the grid + whether it was collapsed or not
- The position of each player

But considering the amount of different possibilities for each card's value + collapsed status + player position, the total number of possible states in **massive**, far beyond what is practical for how many cycles I want to run.

Tabular q-learning works by encountering the same state(s) over
and over and learning what to do in each state. It is "discrete", which is to say, it treats every unique state as totally unrelated.

My initial results were pretty bad. The agent would only win 50% of games.
So, to try to get better results, I needed to either:
1) Reduce the number of possible states by simplifying what goes into the state, or
2) Change away from tabular q-learning to a new approach that isn't discrete (Deep Q-Learning)

### Adaption 1: Reduce state space
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

Even with this reduced state space, I still struggled to beat a 51% win rate.

### Adaption 2: DQN

I added a new, different agent. A DQN-based agent.
This agent uses a 3-layer MLP to accomplish DQN Q-learning.

I also made tweaks to agent rewards (such as, rewarding the agent when it makes a play that reduces the number of possible moves the opponent can take, i.e, cornering/trapping the opponent).

Playing this agent against the random opponent, I was able to achieve a 56% win rate after 100,000 games!

This may not seem that impressive, but I was finally noticing a trend where the agent's win rate would, on average, increase instead of flatlining around 50-51%.

So I am optimistic that with more training and tweaking, I can achieve better results...