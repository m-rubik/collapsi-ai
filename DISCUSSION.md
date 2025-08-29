## Initial Approach
My initial approach was as follows
1. Simulate the game
2. Add a simple tabular Q-learning agent to play the game against a bot that only takes random moves
3. Train the agent to learn to play and consistently beat the "random" opponent

## Findings

Simulating the game in Python is fairly straight-forwarded. The challenge began when I started work on the Q-learning agents.

### Tabular Q-learning
> [This article](https://www.datacamp.com/tutorial/introduction-q-learning-beginner-tutorial) by *Abid Ali Awan* for *datacamp.com* provides an excellent primer on tabular Q-learning

After implementing my tabular Q-learning agent, it became very evident to me how much tabular Q-learning struggles when the state spaces is large.

If you treat the agent like you would treat a human playing the game, as in, you make
the state contain all the information a human would have, the possible number of unique states is **huge**, given the random layout of the cards, the possible position for each player, and the possible collapsed/non-collapsed state of each card. 

At first, my state contained all of this information. Unfortunately, this means that the total number of possible states is **astronomical**, far beyond what is practical for tabular Q-learning, since the tabular approach is discrete, so whole the methodology relies on encountering the same state multiple times to properly train on it.

So, it is not surprising to find that my initial agent would only win 50% of games against the random bot, i.e, it too was playing *effectively* randomly as it never got the opportunity to properly train.

I needed to adapt.

### Adaption 1: Reduce the state space size
---
#### Method
Instead of tracking every card value, what if I just tracked whether each card is collapsed or not?

In a standard setup, the board is 4×4 = 16 cards, and each card can be collapsed (True) or not (False), therefore:

Total collapsed card combinations = 2^16 = 65,536

With 2 players, players can be on any of the 16 tiles except the collapsed ones.

For worst-case estimation, ignore that constraint (i.e., estimate the max possible).

So, both players have 16 possible positions, but they can't be in the same position concurrently, so subtract invalid ones

Total player position pairs: 16 × 15 = 240

Therefore, total state space = collapsed_combinations × player_position_pairs
= 65,536 × 240
= 15,728,640

So **~16 million possible unique states** in this state encoding. This is a much more manageable number.

Additionaly, in real games, it is likely to find that:
- Many states are unreachable (e.g., both players on collapsed tiles)
- Many states are repeated (e.g., early-game setups)

So the effective/realistic state space size is likely less that 16 million, but let's assume worst-case.


#### Outcome
Unfortunately, Even with this reduced state space, I still struggled to beat a 51% win rate.
Likely, I would need to train much more than I did, and I would have to tweak the agent parameters accordingly.

I spent quite a while in this area, trying to make improvements, when I had a new idea...

### Adaption 2: DQN
---
Instead of trying to force a tabular approach, I changed gears and implemented a DQN-based agent.
This agent uses a 3-layer MLP to accomplish DQN Q-learning.

> [This article](https://markelsanz14.medium.com/introduction-to-reinforcement-learning-part-3-q-learning-with-neural-networks-algorithm-dqn-1e22ee928ecd) by *Markel Sanz Ausin* for *medium.com* gives an excellent overview of DQN.

In doing so, I also made tweaks to agent rewards (such as, rewarding the agent when it makes a play that reduces the number of possible moves the opponent can take, i.e, cornering/trapping the opponent). I was very careful in how I approached this, as this was starting to border into coding strategy into the bot, which I wanted to avoid.

After implementing the DQN aganet and training it, I had it play against the random bot, and I was able to achieve a 56% win rate after 100,000 games.

This may not seem that impressive, but I was finally noticing a trend where the agent's win rate would, on average, increase instead of flatlining around 50-51%.

This made me optimistic, it seemed to indicate that with enough training and tweaking, the agent could continue to learn and play better.

Unfortunately, after running 500,000 additional training games, the agent stabilized at a 55.6% win rate. So there was more work to be done, and I had some ideas (beyond reward and model parameter tweaking)...

#### Adaption 2.5: DQN Prioritized Replay Buffer (PRB)

Without PRB, I would be randomly selecting a batch of samples from the buffer to train on.

Instead of randomly selecting the samples, I implemented a prioritized replay buffer, which attempts to pull samples that it thinks it can learn the most from when it comes time to run a training cycle of the underlying MLP.

Unfortunately, even with this in place, I was still getting stuck around the 56% win rate.

Then it occured to me...

## A Brand New Approach

I didn't need to use Q-learning at all. *Collapsi* is a **finite combinatorial game**.

> [Combinatorial Game Theory](https://en.wikipedia.org/wiki/Combinatorial_game_theory) is a fascinating branch of mathematics that dives far deeper into the world of game theory than needed to analyse *Collapsi*.

Because of this, I didn't need to use reinforcement learning to train any sort of agent. Instead, I can use recursive game-tree analysis with memoization to traverse through the game-tree given any particular game state until either:
1. A single winning path is found
2. No winning path is available (unavoidable loss, assuming opponent plays perfectly)

The reason I want to stop once a single winning path is found is because it is far too computationally expensive, and not required, to traverse every single path to find all winning paths.

Then, I can write a bot that on each one of its turns will either:
1. Find a winning path, and take the move that leads into this path
2. Find it has no winning path, take a random move (and hope the opponent blunders)

### Collapsi Solver-Bot (CSB)

#### Features
1. Canonical Game State Representation
    - Each game state is transformed into a hashable canonical form for memoization.
        
        Includes:
        - Board layout: value and collapsed status of each card.
        - Current player index.
        - Player positions on the board.

        This ensures that repeated positions are recognized and redundant computations are avoided.

2. Recursive Solver
    - The core function ```solve(game_state)```:
        - Checks if the current state is terminal (a win/loss) and returns immediately.
        - Generates all valid moves for the current player.
        - Recursively simulates each move using a deep copy of the game state.
        - Determines if there exists any move that guarantees a win by forcing the opponent into a losing position.
        - Uses memoization to cache previously evaluated states, dramatically reducing computation time.

3. Best Move Calculation
    - The ```best_moves(game_state)``` function:
        - Returns a tuple ```(is_winning, winning_moves)```.
        - ```is_winning``` is True if the current player can force a win from the current state.
        - ```winning_moves``` is a list of all moves that guarantee victory, or empty if the position is losing.

4. Interactive Bot Play
    - The bot can play interactively against a human player:
        - Prompts the human for moves.
        - Uses the solver to select the optimal move for itself.
        - If no winning move exists, it chooses a random valid move.
        - Fully supports arbitrary starting boards and any valid player position.

5. Optimization Considerations
    - Canonicalization and memoization drastically reduce repeated computation.
    - Solver works with any arbitrary state of the board.
    - Deep copies ensure the original game state remains unmodified during recursive simulations.
    - Storing all winning moves allows the bot to choose randomly among them for variety.

#### Findings

- If you have two CSB's playing each other, the one that starts the game first has ~33% win rate, compared to the one that starts second. This indicates the game has a bias in favour of the player who plays second.
- Against a random bot, the CSB wins 96.3% (tested on 1000 games).
- Against a human (me), the CSB is incredibly challenging, it took me ~25 games before I managed to beat it.