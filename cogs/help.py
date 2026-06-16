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

        # Match Commands
        embed.add_field(
            name="🎮 Match Commands",
            value=(
                "`bd match [points]` - Start a new doubles match (11 or 21 points)\n"
                "`bd shot <type>` - Play a shot during match (smash, drop, clear, net, drive)\n"
            ),
            inline=False
        )

        # Player Stats Commands
        embed.add_field(
            name="📊 Stats & Profile",
            value=(
                "`bd stats` - View your personal statistics\n"
                "`bd profile [@user]` - View detailed player profile\n"
                "`bd leaderboard` - See top 10 players globally\n"
                "`bd reset_stats` - Reset your stats (irreversible)\n"
            ),
            inline=False
        )

        # Game Info
        embed.add_field(
            name="ℹ️ Game Information",
            value=(
                "`bd info` - Learn about game mechanics\n"
                "`bd shots` - Detailed shot descriptions\n"
                "`bd rules` - Badminton GURU rules\n"
            ),
            inline=False
        )

        embed.set_footer(text="Prefix: bd | Example: bd match 21")
        await ctx.send(embed=embed)

    @commands.command(name="info")
    async def game_info(self, ctx):
        """Show game information and mechanics"""
        embed = discord.Embed(
            title="🏸 About Badminton GURU",
            description="A competitive Discord bot for virtual badminton doubles matches",
            color=discord.Color.cyan()
        )

        embed.add_field(
            name="📋 Game Format",
            value=(
                "**Doubles Matches Only**: 2v2 (you control one side)\n"
                "**Point System**: Win to 11 or 21 points (win by 2)\n"
                "**Rally-Based**: Each shot leads to a rally outcome\n"
                "**Stamina System**: Manage energy across shots\n"
            ),
            inline=False
        )

        embed.add_field(
            name="🎯 How to Play",
            value=(
                "1. Start: `bd match 21` (or 11 for quicker games)\n"
                "2. Play: `bd shot smash` (or drop, clear, net, drive)\n"
                "3. Rally: AI calculates shot success and opponent response\n"
                "4. Win: First team to reach point limit (with 2-point lead)\n"
            ),
            inline=False
        )

        embed.add_field(
            name="⭐ Ranking System",
            value=(
                "🌱 Beginner: 0 RP\n"
                "📈 Intermediate: 100+ RP\n"
                "🎯 Advanced: 200+ RP\n"
                "⭐ Expert: 300+ RP\n"
                "👑 Master: 400+ RP\n"
                "🏆 Champion: 500+ RP\n"
            ),
            inline=False
        )

        await ctx.send(embed=embed)

    @commands.command(name="shots")
    async def show_shots(self, ctx):
        """Detailed explanation of each shot type"""
        embed = discord.Embed(
            title="🎯 Shot Types & Statistics",
            description="Learn about each shot and when to use them",
            color=discord.Color.cyan()
        )

        shots = [
            {
                "name": "💥 Smash",
                "power": "90",
                "stamina": "80",
                "accuracy": "60",
                "risk": "High",
                "use": "Aggressive finishing shot from back court"
            },
            {
                "name": "🪶 Drop",
                "power": "30",
                "stamina": "30",
                "accuracy": "75",
                "risk": "Low",
                "use": "Precision shot to front net, opponent fatigue"
            },
            {
                "name": "✨ Clear",
                "power": "70",
                "stamina": "50",
                "accuracy": "70",
                "risk": "Medium",
                "use": "Defensive deep shot to push opponent back"
            },
            {
                "name": "🕸️ Net Shot",
                "power": "20",
                "stamina": "40",
                "accuracy": "85",
                "risk": "Medium",
                "use": "Delicate placement shot at the net"
            },
            {
                "name": "⚡ Drive",
                "power": "75",
                "stamina": "60",
                "accuracy": "65",
                "risk": "Medium-High",
                "use": "Fast-paced attacking shot mid-court"
            }
        ]

        for shot in shots:
            embed.add_field(
                name=shot["name"],
                value=(
                    f"**Power**: {shot['power']} | **Accuracy**: {shot['accuracy']} | **Risk**: {shot['risk']}\n"
                    f"**Stamina Cost**: {shot['stamina']}\n"
                    f"**Use**: {shot['use']}\n"
                ),
                inline=False
            )

        embed.set_footer(text="Choose shots strategically based on match situation!")
        await ctx.send(embed=embed)

    @commands.command(name="rules")
    async def show_rules(self, ctx):
        """Display game rules"""
        embed = discord.Embed(
            title="⚖️ Badminton GURU Rules",
            color=discord.Color.gold()
        )

        embed.add_field(
            name="🏸 Scoring",
            value=(
                "• Rally-based scoring (winner of each rally scores 1 point)\n"
                "• Choose to play to 11 or 21 points\n"
                "• Win by 2 points if tied at high scores\n"
                "• Match ends immediately when winning condition is met\n"
            ),
            inline=False
        )

        embed.add_field(
            name="⚡ Stamina & Energy",
            value=(
                "• Each shot depletes stamina (based on shot type)\n"
                "• Stamina recovers between rallies\n"
                "• If stamina < shot cost, shot fails and opponent scores\n"
                "• Higher stamina = better shot selection options\n"
            ),
            inline=False
        )

        embed.add_field(
            name="🎯 Shot Mechanics",
            value=(
                "• Each shot has Power, Accuracy, and Risk ratings\n"
                "• Accuracy determines shot success in court\n"
                "• Risk determines opponent's ability to return\n"
                "• Player stats affect shot outcomes\n"
            ),
            inline=False
        )

        embed.add_field(
            name="🤝 Doubles Format",
            value=(
                "• Player controls YOUR side (2 players total)\n"
                "• Partner AI plays alongside you\n"
                "• Opponents are AI-controlled\n"
                "• Shot success depends on player stats\n"
            ),
            inline=False
        )

        embed.add_field(
            name="🏆 Ranking",
            value=(
                "• Wins grant +50 Rank Points\n"
                "• Losses deduct -10 Rank Points\n"
                "• Ranking updates based on RP and win rate\n"
                "• Higher rank unlocks bragging rights!\n"
            ),
            inline=False
        )

        await ctx.send(embed=embed)

    @commands.command(name="tips")
    async def show_tips(self, ctx):
        """Strategy tips for winning"""
        embed = discord.Embed(
            title="💡 Winning Strategies",
            description="Pro tips for becoming a Badminton GURU champion",
            color=discord.Color.green()
        )

        tips = [
            ("🎯 Shot Variety", "Mix up your shots - don't always smash! Drop shots and net shots can tire opponents and set up winners."),
            ("⚡ Stamina Management", "Conserve stamina early in the match. Use low-cost shots (drop, net) to build momentum and save power shots for critical moments."),
            ("🏃 Positioning", "Alternate between front and back court. After aggressive shots, recover to mid-court. Opponent positioning affects their ability to counter."),
            ("📊 Read the Match", "Start defensive against strong opponents. As you gain advantage, switch to aggressive shots. Stay patient on crucial points."),
            ("🔄 Momentum", "Win streaks matter! Build current streaks for confidence. Psychological advantage helps against same-level opponents."),
            ("💪 Player Stats Matter", "Speed affects court coverage. Defense helps returns. Agility improves shot accuracy. Smash Power boosts damage on aggressive shots."),
        ]

        for title, tip in tips:
            embed.add_field(name=title, value=tip, inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(HelpCog(bot))
