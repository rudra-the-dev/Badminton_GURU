import os
from dotenv import load_dotenv

load_dotenv()

DEV_ID = os.getenv("DEV_ID")
WEBSITE_URL = os.getenv("WEBSITE_URL")

# players data
BADMINTON_API_KEY = os.getenv("BADMINTON_API_KEY")

# bot configuration
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
PREFIX = "bdg "

# database configuration
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "BadmintonGuru"

# starting values
STARTING_CURRENCY = 1000
STARTING_PLAYERS = []

# game settings
MIN_POINTS = 11
MAX_POINTS = 21

# ai configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# interface colors
COLOR_PRIMARY = 0x00ACC1   # Badminton cyan
COLOR_SUCCESS = 0x00FF00
COLOR_ERROR = 0xFF0000
COLOR_GOLD = 0xFFD700
