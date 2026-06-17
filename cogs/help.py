import discord
from discord.ext import commands
import random
from datetime import datetime

# Pool of names to generate unique starter players
STARTER_NAMES = [
    "Lin Dan", "Lee Chong Wei", "Viktor Axelsen", "Tai Tzu-ying", 
    "An Se-young", "Carolina Marin", "PV Sindhu", "Kento Momota",
    "Lachsen", "Taufik Hidayat", "Peter Gade", "Lee Zii Jia"
]

class PlayersCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.player_cache = {}

    def generate_random_player(self):
        """Generates a player card dict with balanced stats and calculated OVR"""
        speed = random.randint(65, 85)
        smash_power = random.randint(65, 85)
        defense = random.randint(65, 85)
        agility = random.randint(65, 85)
        ovr = round((speed + smash_power + defense + agility) / 4)
        
        return {
            "name": f"{random.choice(STARTER_NAMES)} #{random.randint(100, 999)}",
            "speed": speed,
            "smash_power": smash_power,
            "defense": defense,
            "agility": agility,
            "ovr": ovr,
            "skill_points": 0
        }

    async def get_player_profile(self, user_id):
        """Fetch a profile document directly from MongoDB"""
        return await self.bot.db.players.find_one({"user_id": user_id})

    @commands.command(name="start")
    async def register_profile(self, ctx):
        """Initialize your Badminton GURU profile and get 1,000 starter coins!"""
        profile = await self.get_player_profile(ctx.author.id)

        if profile:
            await ctx.send("❌ You already have an account! Use `bdg profile` or `bdg stats` to view it.")
            return

        initial_profile = {
            "user_id": ctx.author.id,
            "username": ctx.author.name,
            "coins": 1000,
            "has_claimed_starter": False,
            "inventory": [],
            "matches_played": 0,
            "wins": 0,
            "losses": 0,
            "rank_points": 0,
            "ranking": "Beginner 🌱",
            "created_at": datetime.utcnow()
        }

        await self.bot.db.players.insert_one(initial_profile)

        embed = discord.Embed(
            title="🏸 Account Created!",
            description=f"Welcome to the club manager circuit, **{ctx.author.name}**!",
            color=0x00ACC1
        )
        embed.add_field(name="💰 Starter Bonus", value="**1,000 Coins** has been credited to your account balance.")
        embed.add_field(name="🎁 Next Step", value="Type `bdg claim` to unbox your free Starter Pack containing your first 5 players!", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="claim")
    async def claim_starter_pack(self, ctx):
        """Claim your free starter pack of 5 random players!"""
        profile = await self.get_player_profile(ctx.author.id)

        if not profile:
            await ctx.send("❌ Setup your profile first! Use `bdg start` to register.")
            return

        if profile.get("has_claimed_starter", False):
            await ctx.send("❌ You have already claimed your starter pack cards!")
            return

        # Generate 5 random player cards
        new_cards = [self.generate_random_player() for _ in range(5)]

        await self.bot.db.players.update_one(
            {"user_id": ctx.author.id},
            {
                "$set": {"has_claimed_starter": True},
                "$push": {"inventory": {"$each": new_cards}}
            }
        )

        embed = discord.Embed(
            title="🎁 Pack Opened successfully!",
            description="You have signed 5 new players to your club roster:",
            color=0x00FF00
        )

        for idx, card in enumerate(new_cards, 1):
            embed.add_field(
                name=f"{idx}. {card['name']} (OVR: {card['ovr']})",
                value=f"⚡ SPD: {card['speed']} | 💥 PWR: {card['smash_power']} | 🛡️ DEF: {card['defense']} | 🏃 AGI: {card['agility']}",
                inline=False
            )

        embed.set_footer(text="Your team is ready! Type bdg match to find an opponent.")
        await ctx.send(embed=embed)

    @commands.command(name="stats")
    async def show_stats(self, ctx):
        """Display your current career stats"""
        profile = await self.get_player_profile(ctx.author.id)

        if not profile:
            await ctx.send("❌ Profile not found! Type `bdg start` to create one.")
            return

        embed = discord.Embed(
            title=f"🏸 {ctx.author.name}'s Badminton Stats",
            color=0x00ACC1
        )

        embed.add_field(name="Ranking", value=f"{profile.get('ranking', 'Beginner 🌱')} ({profile.get('rank_points', 0)} RP)", inline=True)
        
        wins = profile.get('wins', 0)
        losses = profile.get('losses', 0)
        played = profile.get('matches_played', 0)
        win_rate = round((wins / max(played, 1)) * 100, 1)
        
        embed.add_field(name="Record", value=f"**{wins}W** - **{losses}L**\n{win_rate}% WR", inline=True)
        embed.add_field(name="Economy", value=f"💰 {profile.get('coins', 0)} Coins", inline=True)
        embed.add_field(name="Inventory Assets", value=f"🎴 {len(profile.get('inventory', []))} Total Players", inline=True)
        embed.add_field(name="Total Matches", value=f"🎮 {played} Played", inline=True)

        await ctx.send(embed=embed)

    @commands.command(name="profile")
    async def show_profile(self, ctx, user: discord.User = None):
        """Show full manager club profile information"""
        target = user or ctx.author
        profile = await self.get_player_profile(target.id)

        if not profile:
            await ctx.send(f"❌ {'You do' if target == ctx.author else f'{target.name} does'} not have an initialized profile setup yet.")
            return

        embed = discord.Embed(title=f"👤 {target.name}'s Manager Hub", color=0x00ACC1)
        embed.add_field(name="🎖️ Ranking Classification", value=f"{profile.get('ranking', 'Beginner 🌱')} ({profile.get('rank_points', 0)} RP)")
        embed.add_field(name="💰 Wallet Balance", value=f"{profile.get('coins', 0)} Coins")
        embed.add_field(name="🏸 Recruited Roster Size", value=f"{len(profile.get('inventory', []))} Player Cards")
        
        wins = profile.get('wins', 0)
        losses = profile.get('losses', 0)
        played = profile.get('matches_played', 0)
        win_rate = round((wins / max(played, 1)) * 100, 1)

        embed.add_field(name="📊 Career Records", value=f"{wins} Wins / {losses} Losses ({win_rate}% Win Rate)", inline=False)
        
        if target.avatar:
            embed.set_thumbnail(url=target.avatar.url)
            
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(PlayersCog(bot))
    
