# Badminton GURU 🏸🎯
A competitive, turn-based PvP Discord bot for virtual badminton doubles matches with full economy profile integration.
## Features
 * **True PvP Doubles Matchmaking**: Challenge real players in your server to an interactive 2v2 doubles format.
 * **Roster Selection Drop-downs**: Hand-pick your player lineup sequentially using interactive Discord dropdown selection lists.
 * **Dynamic Turn-Based Service & Rally Loops**: Active back-and-forth shot calculations (High/Low Services countered by Smashes, Drops, or Lifts).
 * **Tactical Counters**: Integrated mechanics where choosing a bad counter (like lifting a High Service) results in an immediate point loss.
 * **Club Economy Engine**: Register accounts, unbox a free Starter Pack containing 5 unique player assets with randomized OVR stats, and earn coins/skill points.
 * **Balanced Stamina System**: Energy depletes smoothly per rally to impact shot execution variables without causing arbitrary instant failures.
 * **Persistent Data Storage**: Full MongoDB Atlas cloud integration to track your career wins, losses, balances, and global leaderboard status.
## Commands
All commands utilize the unified global prefix: bdg
 * bdg help - View the operational menu and command handbook.
 * bdg start - Initialize your club manager account and claim 1,000 starting coins.
 * bdg claim - Open your free starter pack to sign your first 5 random player cards.
 * bdg match - Post an open matchmaking lobby invite in a channel for an opponent to accept.
 * bdg stats - Review your personal career profile record, win rates, and ranking tier.
 * bdg profile [@user] - Inspect your own or a targeted member's club roster overview.
 * bdg leaderboard - View the top 10 ranked players across the network database.
## Setup
 1. Clone the repository into your local machine environment.
 2. Install the system pack modules via pip.
 3. Establish a localized .env configuration file inside the root directory containing your DISCORD_BOT_TOKEN and MONGO_URI.
 4. Boot up the core system runtime engine by running main.py.
## Game Mechanics
### Match Flow & Rules
 * **Game Point Cap**: Matches are calculated using a strict rally scoring format up to 15 points.
 * **The 7-0 Shutout Clause**: If any side achieves an early lead score of 7-0, the match instantly ends in a shutout victory.
 * **Interactive Turn Sequence**: The serving player picks a service delivery, prompting the receiver with counter buttons. Rallies bounce back and forth based on choice alignments, randomness, and overall rating (OVR) attribute weights.
 * **Match Rewards**: Both contestants receive payouts upon match conclusion (Winners secure higher margins of coins and rank points; losers take smaller participation drops).
 * 
