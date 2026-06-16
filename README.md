# Badminton GURU 🏸🎯

A Discord bot for competitive badminton doubles matches with AI-powered gameplay.

## Features

- **Doubles Match System**: Control your side of the court in 2v2 badminton matches
- **Flexible Point System**: Play to 11 or 21 points (adjustable per match)
- **Rally-Based Gameplay**: Shot selection system (smash, drop, clear, net shot, drive)
- **Player Stats**: Speed, smash power, defense, agility
- **Stamina Mechanics**: Energy depletion based on shot intensity
- **AI Opponents**: Intelligent opponent behavior
- **MongoDB Integration**: Persistent player data and match history

## Commands

- `bd help` - Show all available commands
- `bd match [points]` - Start a doubles match (11 or 21 points)
- `bd stats` - View your player statistics
- `bd leaderboard` - See top players

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with:
   - `DISCORD_BOT_TOKEN`
   - `MONGO_URI`
   - `ANTHROPIC_API_KEY`
4. Run: `python main.py`

## Game Mechanics

### Match Flow
- Player controls one side of doubles court (2v2)
- Each rally: select your shot type
- Points awarded based on rally outcome
- First to 11 or 21 points (win by 2 if tied at 19/20 or 10/9) wins

### Shot Types
- **Smash**: High power, high stamina cost, high risk/reward
- **Drop**: Low power, low stamina, good for net positioning
- **Clear**: Medium power, good for defense
- **Net Shot**: Precise, low stamina, placement-based
- **Drive**: Fast, medium stamina, good pace
