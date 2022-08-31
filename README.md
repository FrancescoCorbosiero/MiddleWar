# MiddleWar

MiddleWar is a simple demo game developed in Pyhton within the pygame library.
Just a little demo to show what pygame is capable of.

## Tech

- Python
- Pygame library

## Installation

MiddleWar requires [Python](https://www.python.org/) v3+ to run.

You can simply download the project and run the command:

```sh
python main.py
```

and game is ready to play!

## Rules and commands
Concept is a tower-defense game in which every player starts with default resources used in order to train troops and invade other player camp. Your camp is composed by Mine for extracting resources, Barrack to train troops and a defensive attacking Tower.

Game is real time, player can chose between these actions:
- train unit
- dispatch unit
- unleash all troops

Units are of 3 types:
- Worker: can either extract gold or restore tower
- Swordsman: short range attacker, takes many turns to be ready to fight
- Archer: long range attacker, takes many turns to be ready to fight

Building unit are of 3 types:
- Tower/Wall: does nothing but protecting the castle and firing arrows
- Barrack: train and hold combat units
- Mine: gives resources through workers

Game units:
- Arrows(Magic crows): fired by archers(horizontal) and towers(diagonal). Cannot change direction

Commands:
- Train:
    - Q/I -> Worker
    - W/O -> Swordsman
    - E/P -> Archer
- Dispatch:
    - A/H -> Worker to mine
    - S/J -> Worker to wall
    - D/K -> Unleash swordsman
    - F/L -> Unleash archer
    - Z/M -> Unleash all
- Pause:
    - Spacebar -> Pauses the game

## Development

Want to contribute? No, I don't think so...
This is just a demo project. Feel free to download and use the project as you wish.

## Pygame library
Pygame allows you to develop simple games in python in a short time.
Here's the main site!: https://www.pygame.org/news
And here's the docs: https://www.pygame.org/docs/

Enjoy!

