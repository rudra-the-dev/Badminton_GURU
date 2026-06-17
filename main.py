# =========================================================================
# PYTHON 3.13+ / 3.14+ COMPATIBILITY PATCH FOR DISCORD.PY
# Discord.py tries to import 'audioop', which was removed in modern Python.
# This injects a dummy module into system memory to bypass the import error.
import sys
from types import ModuleType

if 'audioop' not in sys.modules:
    dummy_audioop = ModuleType('audioop')
    # Provide the basic attributes discord.py looks for
    dummy_audioop.error = Exception
    sys.modules['audioop'] = dummy_audioop
# =========================================================================

import discord
from discord.ext import commands
import motor.motor_asyncio
import config
import os
import asyncio
from flask import Flask
from threading import Thread

# Initialize Intents with Message Content enabled
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=config.PREFIX, intents=intents)

# Flask application layout for web hosting keep-alive pings
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Badminton GURU Bot is alive! 🏸🎯"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    flask_app.run(host='0.0.0.0', port=port)

# Spin up web server thread
Thread(target=run_flask).start()

@bot.event
async def on_ready():
    print(f"=========================================")
    print(f"Logged in successfully as: {bot.user}")
    print(f"Bot Client ID: {bot.user.id}")
    print(f"Prefix configured: '{config.PREFIX}'")
    print(f"=========================================")

async def load_cogs():
    """Dynamically discover and attach cogs from directory"""
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"✅ Extension Loaded: cogs.{filename[:-3]}")
            except Exception as e:
                print(f"❌ Failed to load extension cogs.{filename[:-3]}: {e}")

async def main():
    # Initialize connection handle to MongoDB Atlas
    global client
    client = motor.motor_asyncio.AsyncIOMotorClient(
        config.MONGO_URI,
        tls=True,
        tlsAllowInvalidCertificates=True
    )
    bot.db = client[config.DB_NAME]
    
    try:
        await client.admin.command('ping')
        print("✅ MongoDB connection authenticated successfully!")
    except Exception as e:
        print(f"❌ MongoDB initialization handshake failed: {e}")

    # Load modules and launch event loop
    await load_cogs()  
    await bot.start(config.BOT_TOKEN)

# Launch system routine runtime
if __name__ == "__main__":
    asyncio.run(main())
