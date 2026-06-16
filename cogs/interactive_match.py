import discord
from discord.ext import commands
import asyncio
from cogs.match import Match, ShotType, Team, Player
from cogs.players import PlayerStats

class InteractiveMatchCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_matches = {}
        self.match_sessions = {}

    @commands.command(name="play")
    async def start_interactive_match(self, ctx, max_points: int = 21):
        """Start an interactive doubles badminton match"""
        
        # Validate point selection
        if max_points not in [11, 21]:
            embed = discord.Embed(
                title="❌ Invalid Point Limit",
                description="Please choose either **11** or **21** points",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Check if user already has active match
        if ctx.author.id in self.active_matches:
            await ctx.send("❌ You already have an active match! Finish it first with `bd endmatch`")
            return

        # Create teams
        player1 = Player("You", speed=75, smash_power=78, defense=72, agility=70)
        partner = Player("Your Partner", speed=70, smash_power=73, defense=75, agility=68)
        opponent1 = Player("Opponent 1", speed=72, smash_power=76, defense=70, agility=71)
        opponent2 = Player("Opponent 2", speed=68, smash_power=74, defense=73, agility=69)

        team_player = Team("Your Team", player1, partner)
        team_opponent = Team("Opponents", opponent1, opponent2)

        match = Match(team_player, team_opponent, max_points)
        self.active_matches[ctx.author.id] = match
        self.match_sessions[ctx.author.id] = {
            "started_at": ctx.message.created_at,
            "max_points": max_points,
            "channel": ctx.channel.id
        }

        # Create start embed
        embed = discord.Embed(
            title="🏸 Badminton GURU - Match Start!",
            description=f"First to **{max_points} points** wins (win by 2)",
            color=discord.Color.cyan()
        )

        embed.add_field(
            name="👥 Your Team",
            value=f"**{player1.name}** (SPD: {player1.speed}, PWR: {player1.smash_power})\n**{partner.name}** (SPD: {partner.speed}, PWR: {partner.smash_power})",
            inline=False
        )

        embed.add_field(
            name="🎯 Opponents",
            value=f"**{opponent1.name}** (SPD: {opponent1.speed}, PWR: {opponent1.smash_power})\n**{opponent2.name}** (SPD: {opponent2.speed}, PWR: {opponent2.smash_power})",
            inline=False
        )

        embed.add_field(
            name="📊 Current Score",
            value=f"**Your Team: 0** | **Opponents: 0**",
            inline=False
        )

        embed.add_field(
            name="🎮 How to Play",
            value="Use reactions below to select your shot!\n⚡ = Smash | 🪶 = Drop | ✨ = Clear | 🕸️ = Net | ⚙️ = Drive",
            inline=False
        )

        msg = await ctx.send(embed=embed)
        
        # Add reaction buttons
        reactions = ["💥", "🪶", "✨", "🕸️", "⚡"]
        for reaction in reactions:
            await msg.add_reaction(reaction)

        self.match_sessions[ctx.author.id]["match_message"] = msg

    @commands.command(name="shot")
    async def play_shot_command(self, ctx, shot_name: str = None):
        """Play a shot during an active match"""
        
        if ctx.author.id not in self.active_matches:
            embed = discord.Embed(
                title="❌ No Active Match",
                description="Start a match with `bd play [11/21]`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if not shot_name:
            embed = discord.Embed(
                title="❌ Invalid Shot",
                description="Available shots: **smash**, **drop**, **clear**, **net**, **drive**",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        shot_map = {
            "smash": ShotType.SMASH,
            "drop": ShotType.DROP,
            "clear": ShotType.CLEAR,
            "net": ShotType.NET_SHOT,
            "drive": ShotType.DRIVE
        }

        shot_type = shot_map.get(shot_name.lower())
        if not shot_type:
            await ctx.send(f"❌ Unknown shot: `{shot_name}`. Try: smash, drop, clear, net, drive")
            return

        match = self.active_matches[ctx.author.id]
        success, winner, details = match.execute_rally(match.team1, shot_type)

        if not success:
            await ctx.send(details)
            return

        # Create rally result embed
        embed = discord.Embed(
            title="🏸 Rally Result",
            description=details,
            color=discord.Color.green() if winner == match.team1 else discord.Color.orange()
        )

        embed.add_field(
            name="📊 Score",
            value=match.get_score_display(),
            inline=False
        )

        embed.add_field(
            name="⚡ Stamina",
            value=f"You: {match.team1.player1.stamina}% | Partner: {match.team1.player2.stamina}%",
            inline=True
        )

        embed.add_field(
            name="💪 Opponent Stamina",
            value=f"Opp1: {match.team2.player1.stamina}% | Opp2: {match.team2.player2.stamina}%",
            inline=True
        )

        await ctx.send(embed=embed)

        # Check if match is over
        if match.is_match_over():
            await self._end_match(ctx, match, winner_team=match.winner)

    @commands.command(name="score")
    async def show_score(self, ctx):
        """Show current match score"""
        if ctx.author.id not in self.active_matches:
            await ctx.send("❌ No active match!")
            return

        match = self.active_matches[ctx.author.id]

        embed = discord.Embed(
            title="📊 Current Match Score",
            color=discord.Color.cyan()
        )

        embed.add_field(
            name=f"🎯 {match.team1.name}",
            value=f"**{match.team1.score}** points\nP1: {match.team1.player1.stamina}%\nP2: {match.team1.player2.stamina}%",
            inline=True
        )

        embed.add_field(
            name=f"💪 {match.team2.name}",
            value=f"**{match.team2.score}** points\nP1: {match.team2.player1.stamina}%\nP2: {match.team2.player2.stamina}%",
            inline=True
        )

        embed.add_field(
            name="ℹ️ Match Info",
            value=f"First to: **{match.max_points}** points\nRallies played: **{match.rally_count}**",
            inline=False
        )

        await ctx.send(embed=embed)

    @commands.command(name="endmatch")
    async def end_match(self, ctx):
        """End the current match"""
        if ctx.author.id not in self.active_matches:
            await ctx.send("❌ No active match to end!")
            return

        match = self.active_matches[ctx.author.id]
        await self._end_match(ctx, match)

    async def _end_match(self, ctx, match, winner_team=None):
        """Handle match ending and stats update"""
        if winner_team is None:
            winner_team = match.team1 if match.team1.score > match.team2.score else match.team2

        # Get player stats cog
        players_cog = self.bot.get_cog("PlayersCog")
        stats = await players_cog.get_player_stats(ctx.author.id, ctx.author.name)

        # Update stats
        stats.total_points_scored += match.team1.score
        stats.total_points_conceded += match.team2.score

        if winner_team == match.team1:
            stats.add_win()
        else:
            stats.add_loss()

        # Save to database
        await players_cog.save_player_stats(stats)

        # Create end match embed
        embed = discord.Embed(
            title="🏁 Match Ended!",
            color=discord.Color.gold() if winner_team == match.team1 else discord.Color.red()
        )

        embed.add_field(
            name="🏆 Winner",
            value=winner_team.name,
            inline=False
        )

        embed.add_field(
            name="📊 Final Score",
            value=match.get_score_display(),
            inline=False
        )

        embed.add_field(
            name="📈 Your Stats Update",
            value=f"**Record**: {stats.wins}W - {stats.losses}L\n**Win Rate**: {stats.get_win_rate()}%\n**Rank Points**: {stats.rank_points}\n**Ranking**: {stats.ranking}",
            inline=False
        )

        embed.add_field(
            name="🔥 Streak",
            value=f"Current: {stats.current_streak} | Best: {stats.best_streak}",
            inline=True
        )

        embed.set_footer(text="Use bd stats to see full stats | bd play to start another match!")

        await ctx.send(embed=embed)

        # Clean up
        del self.active_matches[ctx.author.id]
        if ctx.author.id in self.match_sessions:
            del self.match_sessions[ctx.author.id]

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """Handle reaction-based shot selection"""
        if user.bot:
            return

        if user.id not in self.active_matches:
            return

        reaction_map = {
            "💥": "smash",
            "🪶": "drop",
            "✨": "clear",
            "🕸️": "net",
            "⚡": "drive"
        }

        if str(reaction.emoji) not in reaction_map:
            return

        # Remove the reaction
        try:
            await reaction.remove(user)
        except:
            pass

        shot_type = reaction_map[str(reaction.emoji)]
        match = self.active_matches[user.id]

        shot_map = {
            "smash": ShotType.SMASH,
            "drop": ShotType.DROP,
            "clear": ShotType.CLEAR,
            "net": ShotType.NET_SHOT,
            "drive": ShotType.DRIVE
        }

        shot_obj = shot_map[shot_type]
        success, winner, details = match.execute_rally(match.team1, shot_obj)

        if not success:
            embed = discord.Embed(description=details, color=discord.Color.red())
            await reaction.message.reply(embed=embed)
            return

        # Create rally result
        embed = discord.Embed(
            title="🏸 Rally Result",
            description=details,
            color=discord.Color.green() if winner == match.team1 else discord.Color.orange()
        )

        embed.add_field(
            name="📊 Score",
            value=match.get_score_display(),
            inline=False
        )

        embed.add_field(
            name="��� Stamina",
            value=f"You: {match.team1.player1.stamina}% | Partner: {match.team1.player2.stamina}%",
            inline=True
        )

        await reaction.message.reply(embed=embed)

        # Check match end
        if match.is_match_over():
            players_cog = self.bot.get_cog("PlayersCog")
            stats = await players_cog.get_player_stats(user.id, user.name)

            stats.total_points_scored += match.team1.score
            stats.total_points_conceded += match.team2.score

            if match.winner == match.team1:
                stats.add_win()
            else:
                stats.add_loss()

            await players_cog.save_player_stats(stats)

            end_embed = discord.Embed(
                title="🏁 Match Ended!",
                description=f"**{match.winner.name}** wins {match.winner.score}-{match.team1.score if match.winner == match.team2 else match.team2.score}!",
                color=discord.Color.gold()
            )

            end_embed.add_field(
                name="📈 Updated Stats",
                value=f"**Record**: {stats.wins}W - {stats.losses}L ({stats.get_win_rate()}%)\n**Rank**: {stats.ranking} ({stats.rank_points} RP)",
                inline=False
            )

            await reaction.message.reply(embed=end_embed)
            del self.active_matches[user.id]

async def setup(bot):
    await bot.add_cog(InteractiveMatchCog(bot))
