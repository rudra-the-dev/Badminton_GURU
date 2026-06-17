import discord
from discord.ext import commands

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")  
    async def show_help(self, ctx):  
        """Display all available commands"""  
        embed = discord.Embed(  
            title="🏸 Badminton GURU - Command Guide",  
            description="Complete list of commands and how to use them",  
            color=discord.Color.cyan()  
        )  

        # Account / Profile Commands
        embed.add_field(  
            name="👤 Profile & Economy",  
            value=(  
                "`bdg start` - Register your profile and claim 1,000 free starting coins\n"  
                "`bdg claim` - Claim your first free starter pack containing 5 players\n"  
                "`bdg stats` - View your personal statistics\n"  
                "`bdg profile [@user]` - View detailed club manager profile\n"  
                "`bdg leaderboard` - See top 10 players globally\n"  
            ),  
            inline=False  
        )  

        # Match Commands  
        embed.add_field(  
            name="🎮 Match Commands",  
            value=(  
                "`bdg match` - Post a matchmaking challenge for a doubles match\n"  
            ),  
            inline=False  
        )  

        # Game Info  
        embed.add_field(  
            name="ℹ️ Game Information",  
            value=(  
                "`bdg info` - Learn about game mechanics\n"  
                "`bdg shots` - Detailed shot descriptions\n"  
                "`bdg rules` - Badminton GURU rules\n"  
            ),  
            inline=False  
        )  

        embed.set_footer(text="Prefix: bdg | Example: bdg match")  
        await ctx.send(embed=embed)  

    @commands.command(name="info")  
    async def game_info(self, ctx):  
        """Show game information and mechanics"""  
        embed = discord.Embed(  
            title="🏸 About Badminton GURU",  
            description="A competitive, turn-based PvP Discord bot for virtual badminton doubles matches",  
            color=discord.Color.cyan()  
        )  

        embed.add_field(  
            name="📋 Game Format",  
            value=(  
                "**Doubles Match PvP**: 2v2 tactical rallies where you control your card roster lineup.\n"  
                "**Point System**: Played up to 15 points. If a team achieves a 7-0 shutout, they win instantly!\n"  
                "**Rally-Based**: Rallies continue dynamically until someone fails a shot or picks the wrong counter.\n"  
                "**Rewards**: Winning matches rewards you with coins and skill points to upgrade your athletes."  
            ),  
            inline=False  
        )  

        embed.add_field(  
            name="🎯 How to Play",  
            value=(  
                "1. Register: `bdg start` to set up your profile and get 1,000 coins.\n"  
                "2. Recruit: `bdg claim` to open your free pack and obtain your first 5 players.\n"  
                "3. Challenge: Type `bdg match` and wait for another player to accept via the button.\n"  
                "4. Match Flow: Select your 2 players using the drop-downs, service choices, and counter shots!"  
            ),  
            inline=False  
        )  

        await ctx.send(embed=embed)  

    @commands.command(name="shots")  
    async def show_shots(self, ctx):  
        """Detailed explanation of each shot type"""  
        embed = discord.Embed(  
            title="🎯 Action Types & Shots",  
            description="Learn about the primary types of shots you can deploy during live match rallies",  
            color=discord.Color.cyan()  
        )  

        embed.add_field(  
            name="🏸 Services (Server Choice)",  
            value="• **High Service**\n• **Low Service**",  
            inline=False  
        )  

        embed.add_field(  
            name="💥 Counter Shots (Receiver Choice)",  
            value=(  
                "• **Smash It** - Highly aggressive; high risk but high point conversion.\n"  
                "• **Raise / Lift It** - Defensive clearance to push opponents back, but lifting a high service drops your accuracy entirely!\n"  
                "• **Drop / Cut It** - Precision tactical soft touch landing close to the front net."  
            ),  
            inline=False  
        )  

        embed.set_footer(text="Choose counters strategically based on your opponent's incoming shot type!")  
        await ctx.send(embed=embed)  

    @commands.command(name="rules")  
    async def show_rules(self, ctx):  
        """Display game rules"""  
        embed = discord.Embed(  
            title="⚖️ Badminton GURU Rules",  
            color=discord.Color.gold()  
        )  

        embed.add_field(  
            name="🏸 Scoring Conditions",  
            value=(  
                "• Rally-based format: The side that wins the play sequence earns 1 point.\n"  
                "• Matches are played to a standard targeted limit of 15 points.\n"  
                "• **Shutout Rule**: If a match reaches a score of 7-0, the leading team wins immediately.\n"  
                "• Rewards are distributed to both sides at the end, though winners receive higher stakes."  
            ),  
            inline=False  
        )  

        embed.add_field(  
            name="🧠 Match Calculation Engine",  
            value=(  
                "• Shot outcomes are decided by a combination of choice countering matrix logic, "  
                "the Overall Ratings (OVR) of the active players on court, and an engineered factor of randomness."  
            ),  
            inline=False  
        )  

        await ctx.send(embed=embed)  

async def setup(bot):
    await bot.add_cog(HelpCog(bot))
