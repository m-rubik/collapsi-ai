# Collapsi - AI

This project is a fan-made adaptation of the [*Collapsi*](https://riffleshuffleandroll.itch.io/collapsi) board game, developped by Mark from [*Riffle Shuffle & Roll*](https://www.youtube.com/@riffleshuffleandroll), with the aim of developing a bot that learns how to play the game.

What started as an experiment with various Q-Learning techniques evolved into an exercise in game theory. Realising that *Collapsi* is a finite combinatorial game, I was able to use recursive game-tree analysis with memoization to develop a bot that played the game by analysing the game-tree for every game state.

## About Collapsi
From the [Riffle Shuffle & Roll](https://riffleshuffleandroll.itch.io/collapsi) website:
> Collapsi is an abstract strategy maze game for two (or more?) players.  As players move around the grid, the card they move from collapses, causing the grid to slowly close in on itself.  Use portals and cave-ins to your advantage. Trap your opponent and be the last player able to make a legal move to win the game.

## Purpose of This Project

The goal of this project is to implement a modified version of *Collapsi* in a Python environment, to allow for the creation of a bot that learns how to play the game. Ultimately, I hope to generate a bot that poses a significant challenge for a human to play against.

The key pillars guiding this work:
- I will not educate the bot on any strategies for winning. I will only inform it of the rules of the game, and allow it to determine for itself how it wishes to play.
- I will start by exploring Q-learning implementations, and progress from there
- I will consider the success of this project as follows:
    1. Can the trained bot *consistently* beat a random bot (i.e, a bot that takes a random action on each of its turns)?
    2. Can the trained bot pose a significant challenge to a human player?

## Results

For details, see [DISCUSSION.md](DISCUSSION.md).

---
## Legal Notice

This project is not an official adaptation, is non-commercial, and is intended purely for educational and research purposes. Certain game mechanics and elements may have been modified or omitted in this version of the game.

All intellectual property rights related to *Collapsi* are the property of Riffle Shuffle & Roll. This project does not claim ownership of any of the original game content and is in no way affiliated with or endorsed by Riffle Shuffle & Roll.

If you would like to support the official *Collapsi* game, please visit [Riffle Shuffle & Roll](https://riffleshuffleandroll.itch.io/collapsi).
