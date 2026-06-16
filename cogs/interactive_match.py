import discord
from discord.ext import commands
import asyncio
import random
from cogs.match import Match, ShotType, Team, Player
from cogs.players import PlayerStats

class CommentaryGenerator:
    """Generate realistic badminton match commentary"""
    
    @staticmethod
    def get_shot_commentary(player_name, shot_type, success, rally_winner=None):
        """Generate commentary for a shot"""
        commentaries = {
            ShotType.SMASH: {
                "success": [
                    f"💥 {player_name} unleashes a POWERFUL SMASH! The shuttlecock flies like a bullet!",
                    f"⚡ MASSIVE SMASH from {player_name}! What power!",
                    f"🔥 {player_name} goes for the kill with a devastating SMASH!",
                    f"💪 BOOM! {player_name} fires an aggressive SMASH down the line!",
                ],
                "fail": [
                    f"❌ {player_name} attempts a smash but it goes OUT! Too ambitious!",
                    f"😅 {player_name}'s smash is too powerful - it clears the baseline!",
                    f"⚠️ {player_name} goes for broke with the smash... but it's wide!",
                ]
            },
            ShotType.DROP: {
                "success": [
                    f"🪶 Delicate DROP shot from {player_name}! It barely clears the net!",
                    f"✨ Beautiful touch! {player_name} plays a precision DROP to the front court!",
                    f"🎯 {player_name} cuts the pace with a clever DROP shot!",
                    f"👌 Masterful DROP from {player_name}! The opponents are caught off-guard!",
                ],
                "fail": [
                    f"❌ {player_name}'s drop shot doesn't make it over the net!",
                    f"😞 The drop falls short - that's in the net!",
                    f"⚠️ {player_name} attempts a drop but can't control it!",
                ]
            },
            ShotType.CLEAR: {
                "success": [
                    f"✨ {player_name} sends a high CLEAR to the back! Good defensive play!",
                    f"📌 Strong CLEAR from {player_name}! Pushing the opponents deep!",
                    f"🛡️ {player_name} plays a defensive CLEAR to reset the rally!",
                    f"💨 Fast-paced CLEAR from {player_name}! The shuttle goes deep!",
                ],
                "fail": [
                    f"❌ {player_name}'s clear goes too far - it's OUT!",
                    f"⚠️ The clear attempt is too high - the opponents can attack!",
                ]
            },
            ShotType.NET_SHOT: {
                "success": [
                    f"🕸️ Exquisite NET SHOT from {player_name}! So much finesse!",
                    f"💎 {player_name} plays a delicate net shot with perfect placement!",
                    f"🎪 Incredible precision from {player_name}! That net shot was surgical!",
                    f"✨ {player_name} places a soft net shot just over the tape!",
                ],
                "fail": [
                    f"❌ {player_name}'s net shot catches the tape and falls back!",
                    f"😞 Just barely - the net shot is too short!",
                ]
            },
            ShotType.DRIVE: {
                "success": [
                    f"⚡ Fast DRIVE from {player_name}! Flat and aggressive!",
                    f"🏹 {player_name} crushes a quick DRIVE! The pace is unreal!",
                    f"💨 Rapid-fire DRIVE from {player_name}! No time to react!",
                    f"⚡ {player_name} goes for pace with a blistering DRIVE!",
                ],
                "fail": [
                    f"❌ {player_name}'s drive goes into the net!",
                    f"⚠️ The drive is too aggressive - it flies out!",
                ]
            }
        }
        
        shot_name = shot_type.name
        commentary_list = commentaries.get(shot_type, {}).get("success" if success else "fail", [])
        return random.choice(commentary_list) if commentary_list else f"{shot_name} attempt by {player_name}"

    @staticmethod
    def get_rally_outcome_commentary(winning_team_name, losing_player_name, point_type):
        """Generate commentary for rally outcome"""
        outcomes = [
            f"🎯 **POINT!** {winning_team_name} takes the rally! The pressure mounts!",
            f"✅ **SCORE!** Excellent play from {winning_team_name}!",
            f"🏆 **POINT TO {winning_team_name}!** They extend their lead!",
            f"💪 **{winning_team_name} SCORES!** Momentum swinging their way!",
            f"🔥 **POINT!** {winning_team_name} is on fire right now!",
            f"📈 **SCORE!** {winning_team_name} keeps building pressure!",
        ]
        return random.choice(outcomes)

    @staticmethod
    def get_match_commentary(team1_score, team2_score, max_points):
        """Generate match situation commentary"""
        total = team1_score + team2_score
        
        if total == 0:
            return "🏸 Here we go! Both teams ready. This will be INTENSE!"
        
        diff = abs(team1_score - team2_score)
        
        if team1_score == max_points - 1 or team2_score == max_points - 1:
            return "🔥 WE'RE ON THE EDGE! One team is ONE POINT away from victory!"
        
        if diff >= 5:
            leader = "Your Team" if team1_score > team2_score else "Opponents"
            return f"📊 {leader} is DOMINATING! Building a commanding lead!"
        
        if diff == 0:
            return "⚖️ TIED! The momentum could shift at any moment!"
        
        if diff == 1:
            return "🎯 CLOSE MATCH! Every point matters!"
        
        return "💨 The pace is intense! Both teams are fighting hard!"

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
            "channel": ctx.channel.id,
            "rally_count": 0
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
            name="🎮 Select Your Shot",
            value="Click a button below to play!\n💥 Smash | 🪶 Drop | ✨ Clear | 🕸️ Net Shot | ⚡ Drive",
            inline=False
        )

        msg = await ctx.send(embed=embed)
        
        # Create buttons using views
        view = ShotSelectionView(self.bot, ctx.author.id, match, self.active_matches, self.match_sessions)
        await msg.edit(view=view)
        
        self.match_sessions[ctx.author.id]["match_message"] = msg

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
            value=f"**{match.team1.score}** points\nP1 Stamina: {match.team1.player1.stamina}%\nP2 Stamina: {match.team1.player2.stamina}%",
            inline=True
        )

        embed.add_field(
            name=f"💪 {match.team2.name}",
            value=f"**{match.team2.score}** points\nP1 Stamina: {match.team2.player1.stamina}%\nP2 Stamina: {match.team2.player2.stamina}%",
            inline=True
        )

        embed.add_field(
            name="ℹ️ Match Info",
            value=f"First to: **{match.max_points}** points\nRallies played: **{match.rally_count}**\n{CommentaryGenerator.get_match_commentary(match.team1.score, match.team2.score, match.max_points)}",
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

class ShotSelectionView(discord.ui.View):
    """Interactive buttons for shot selection"""
    
    def __init__(self, bot, user_id, match, active_matches, match_sessions):
        super().__init__(timeout=None)
        self.bot = bot
        self.user_id = user_id
        self.match = match
        self.active_matches = active_matches
        self.match_sessions = match_sessions

    @discord.ui.button(label="Smash", emoji="💥", style=discord.ButtonStyle.red)
    async def smash_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.execute_shot(interaction, ShotType.SMASH)

    @discord.ui.button(label="Drop", emoji="🪶", style=discord.ButtonStyle.blurple)
    async def drop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.execute_shot(interaction, ShotType.DROP)

    @discord.ui.button(label="Clear", emoji="✨", style=discord.ButtonStyle.green)
    async def clear_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.execute_shot(interaction, ShotType.CLEAR)

    @discord.ui.button(label="Net Shot", emoji="🕸️", style=discord.ButtonStyle.blurple)
    async def net_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.execute_shot(interaction, ShotType.NET_SHOT)

    @discord.ui.button(label="Drive", emoji="⚡", style=discord.ButtonStyle.danger)
    async def drive_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.execute_shot(interaction, ShotType.DRIVE)

    async def execute_shot(self, interaction: discord.Interaction, shot_type: ShotType):
        """Execute a rally with the selected shot"""
        await interaction.response.defer()

        if interaction.user.id != self.user_id:
            await interaction.followup.send("❌ This is not your match!", ephemeral=True)
            return

        if self.user_id not in self.active_matches:
            await interaction.followup.send("❌ Match not found!", ephemeral=True)
            return

        match = self.active_matches[self.user_id]
        
        # Execute rally
        success, winner, rally_details = match.execute_rally(match.team1, shot_type)

        if not success:
            embed = discord.Embed(
                description=rally_details,
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return

        # Create detailed commentary embed
        embed = discord.Embed(
            title="🏸 Rally in Progress...",
            color=discord.Color.fuchsia()
        )

        # Shot commentary
        shot_commentary = CommentaryGenerator.get_shot_commentary(
            match.team1.player1.name,
            shot_type,
            True,
            winner
        )
        embed.add_field(name="🎙️ Shot Played", value=shot_commentary, inline=False)

        # Rally outcome
        rally_outcome = CommentaryGenerator.get_rally_outcome_commentary(
            winner.name,
            match.team2.player1.name if winner == match.team1 else match.team1.player1.name,
            "rally"
        )
        embed.add_field(name="📊 Rally Outcome", value=rally_outcome, inline=False)

        # Current score
        embed.add_field(
            name="📈 Score Update",
            value=match.get_score_display(),
            inline=False
        )

        # Stamina status
        embed.add_field(
            name="⚡ Team Stamina",
            value=f"**Your Team**: {match.team1.player1.name} {match.team1.player1.stamina}% | {match.team1.player2.name} {match.team1.player2.stamina}%\n**Opponents**: {match.team2.player1.name} {match.team2.player1.stamina}% | {match.team2.player2.name} {match.team2.player2.stamina}%",
            inline=False
        )

        # Match situation
        situation = CommentaryGenerator.get_match_commentary(
            match.team1.score,
            match.team2.score,
            match.max_points
        )
        embed.add_field(name="🎤 Commentary", value=situation, inline=False)

        embed.set_footer(text="Select your next shot!")

        await interaction.followup.send(embed=embed)

        # Check if match is over
        if match.is_match_over():
            players_cog = self.bot.get_cog("PlayersCog")
            stats = await players_cog.get_player_stats(interaction.user.id, interaction.user.name)

            stats.total_points_scored += match.team1.score
            stats.total_points_conceded += match.team2.score

            if match.winner == match.team1:
                stats.add_win()
            else:
                stats.add_loss()

            await players_cog.save_player_stats(stats)

            end_embed = discord.Embed(
                title="🏁 MATCH OVER!",
                description=f"🏆 **{match.winner.name.upper()}** WINS!",
                color=discord.Color.gold()
            )

            end_embed.add_field(
                name="📊 Final Score",
                value=match.get_score_display(),
                inline=False
            )

            end_embed.add_field(
                name="📈 Your Updated Stats",
                value=f"**Record**: {stats.wins}W - {stats.losses}L ({stats.get_win_rate()}%)\n**Ranking**: {stats.ranking} ({stats.rank_points} RP)\n**Streak**: {stats.current_streak}🔥 (Best: {stats.best_streak})",
                inline=False
            )

            end_embed.set_footer(text="Type bd play to start another match!")

            await interaction.followup.send(embed=end_embed)
            del self.active_matches[interaction.user.id]

async def setup(bot):
    await bot.add_cog(InteractiveMatchCog(bot))
