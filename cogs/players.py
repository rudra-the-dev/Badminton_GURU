import discord
from discord.ext import commands
from datetime import datetime

class PlayerStats:
    def __init__(self, user_id, username):
        self.user_id = user_id
        self.username = username
        self.matches_played = 0
        self.wins = 0
        self.losses = 0
        self.total_points_scored = 0
        self.total_points_conceded = 0
        self.smash_accuracy = 0
        self.drop_accuracy = 0
        self.clear_accuracy = 0
        self.net_accuracy = 0
        self.drive_accuracy = 0
        self.best_streak = 0
        self.current_streak = 0
        self.created_at = datetime.now()
        self.ranking = "Beginner"
        self.rank_points = 0

    def add_win(self):
        self.wins += 1
        self.matches_played += 1
        self.current_streak += 1
        self.best_streak = max(self.best_streak, self.current_streak)
        self.rank_points += 50
        self._update_ranking()

    def add_loss(self):
        self.losses += 1
        self.matches_played += 1
        self.current_streak = 0
        self.rank_points = max(0, self.rank_points - 10)
        self._update_ranking()

    def _update_ranking(self):
        """Update player ranking based on win rate and rank points"""
        if self.matches_played == 0:
            self.ranking = "Beginner"
        else:
            win_rate = (self.wins / self.matches_played) * 100
            
            if self.rank_points >= 500 and win_rate >= 70:
                self.ranking = "Champion 🏆"
            elif self.rank_points >= 400 and win_rate >= 65:
                self.ranking = "Master 👑"
            elif self.rank_points >= 300 and win_rate >= 60:
                self.ranking = "Expert ⭐"
            elif self.rank_points >= 200 and win_rate >= 55:
                self.ranking = "Advanced 🎯"
            elif self.rank_points >= 100 and win_rate >= 50:
                self.ranking = "Intermediate 📈"
            else:
                self.ranking = "Beginner 🌱"

    def get_win_rate(self):
        if self.matches_played == 0:
            return 0
        return round((self.wins / self.matches_played) * 100, 2)

    def to_dict(self):
        """Convert to dict for MongoDB storage"""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "matches_played": self.matches_played,
            "wins": self.wins,
            "losses": self.losses,
            "total_points_scored": self.total_points_scored,
            "total_points_conceded": self.total_points_conceded,
            "smash_accuracy": self.smash_accuracy,
            "drop_accuracy": self.drop_accuracy,
            "clear_accuracy": self.clear_accuracy,
            "net_accuracy": self.net_accuracy,
            "drive_accuracy": self.drive_accuracy,
            "best_streak": self.best_streak,
            "current_streak": self.current_streak,
            "ranking": self.ranking,
            "rank_points": self.rank_points,
            "created_at": self.created_at
        }

class PlayersCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.player_cache = {}

    async def get_player_stats(self, user_id, username):
        """Get or create player stats"""
        if user_id in self.player_cache:
            return self.player_cache[user_id]

        # Try to fetch from database
        db = self.bot.db
        player_doc = await db.players.find_one({"user_id": user_id})

        if player_doc:
            stats = PlayerStats(user_id, username)
            stats.matches_played = player_doc.get("matches_played", 0)
            stats.wins = player_doc.get("wins", 0)
            stats.losses = player_doc.get("losses", 0)
            stats.total_points_scored = player_doc.get("total_points_scored", 0)
            stats.total_points_conceded = player_doc.get("total_points_conceded", 0)
            stats.ranking = player_doc.get("ranking", "Beginner")
            stats.rank_points = player_doc.get("rank_points", 0)
            stats.best_streak = player_doc.get("best_streak", 0)
            stats.current_streak = player_doc.get("current_streak", 0)
        else:
            stats = PlayerStats(user_id, username)
            await db.players.insert_one(stats.to_dict())

        self.player_cache[user_id] = stats
        return stats

    async def save_player_stats(self, stats):
        """Save player stats to database"""
        db = self.bot.db
        await db.players.update_one(
            {"user_id": stats.user_id},
            {"$set": stats.to_dict()},
            upsert=True
        )
        self.player_cache[stats.user_id] = stats

    @commands.command(name="stats")
    async def show_stats(self, ctx):
        """Display your badminton stats"""
        stats = await self.get_player_stats(ctx.author.id, ctx.author.name)

        embed = discord.Embed(
            title=f"🏸 {ctx.author.name}'s Badminton Stats",
            color=discord.Color.cyan()
        )

        embed.add_field(
            name="Ranking",
            value=f"{stats.ranking}\n{stats.rank_points} RP",
            inline=True
        )

        embed.add_field(
            name="Record",
            value=f"**{stats.wins}**W - **{stats.losses}**L\n{stats.get_win_rate()}% WR",
            inline=True
        )

        embed.add_field(
            name="Streaks",
            value=f"Current: **{stats.current_streak}** 🔥\nBest: **{stats.best_streak}**",
            inline=True
        )

        embed.add_field(
            name="Points",
            value=f"Scored: **{stats.total_points_scored}**\nConceded: **{stats.total_points_conceded}**",
            inline=True
        )

        embed.add_field(
            name="Matches",
            value=f"**{stats.matches_played}** total",
            inline=True
        )

        embed.add_field(
            name="Member Since",
            value=f"<t:{int(stats.created_at.timestamp())}:R>",
            inline=True
        )

        embed.set_thumbnail(url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="leaderboard")
    async def show_leaderboard(self, ctx):
        """Show top 10 players by ranking"""
        db = self.bot.db
        top_players = await db.players.find().sort("rank_points", -1).limit(10).to_list(None)

        if not top_players:
            await ctx.send("📊 No players yet! Be the first to `bd match` and climb the ranks!")
            return

        embed = discord.Embed(
            title="🏸 Badminton GURU Leaderboard",
            description="Top 10 Players",
            color=discord.Color.gold()
        )

        leaderboard_text = ""
        for i, player in enumerate(top_players, 1):
            win_rate = 0
            if player["matches_played"] > 0:
                win_rate = round((player["wins"] / player["matches_played"]) * 100, 1)

            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"#{i}"

            leaderboard_text += (
                f"{medal} **{player['username']}** ({player['ranking']})\n"
                f"  └─ {player['rank_points']} RP | {player['wins']}W-{player['losses']}L ({win_rate}%)\n\n"
            )

        embed.description = leaderboard_text
        embed.set_footer(text="Ranked by: Rank Points")
        await ctx.send(embed=embed)

    @commands.command(name="profile")
    async def show_profile(self, ctx, user: discord.User = None):
        """Show detailed player profile"""
        target = user or ctx.author
        stats = await self.get_player_stats(target.id, target.name)

        embed = discord.Embed(
            title=f"👤 {target.name}'s Profile",
            color=discord.Color.blue()
        )

        embed.set_thumbnail(url=target.avatar.url)

        # Rank info
        embed.add_field(
            name="🎖️ Rank",
            value=f"{stats.ranking}\n**{stats.rank_points}** Rank Points",
            inline=False
        )

        # Match record
        embed.add_field(
            name="📊 Match Record",
            value=(
                f"Matches: **{stats.matches_played}**\n"
                f"Wins: **{stats.wins}**\n"
                f"Losses: **{stats.losses}**\n"
                f"Win Rate: **{stats.get_win_rate()}%**"
            ),
            inline=True
        )

        # Streaks
        embed.add_field(
            name="🔥 Streaks",
            value=(
                f"Current: **{stats.current_streak}**\n"
                f"Best: **{stats.best_streak}**"
            ),
            inline=True
        )

        # Points
        embed.add_field(
            name="📍 Points Statistics",
            value=(
                f"Total Scored: **{stats.total_points_scored}**\n"
                f"Total Conceded: **{stats.total_points_conceded}**\n"
                f"Avg per Match: **{round(stats.total_points_scored / max(stats.matches_played, 1), 1)}**"
            ),
            inline=False
        )

        embed.set_footer(text=f"Member since {stats.created_at.strftime('%B %d, %Y')}")
        await ctx.send(embed=embed)

    @commands.command(name="reset_stats")
    async def reset_stats(self, ctx):
        """Reset your stats (confirmation required)"""
        embed = discord.Embed(
            title="⚠️ Reset Statistics",
            description="Are you sure? This will reset all your stats to 0.",
            color=discord.Color.red()
        )

        msg = await ctx.send(embed=embed)
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["✅", "❌"]

        try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout=30.0, check=check)
            if str(reaction.emoji) == "✅":
                db = self.bot.db
                await db.players.delete_one({"user_id": ctx.author.id})
                if ctx.author.id in self.player_cache:
                    del self.player_cache[ctx.author.id]
                await ctx.send("✅ Your stats have been reset!")
            else:
                await ctx.send("❌ Reset cancelled.")
        except:
            await ctx.send("⏱️ Reset confirmation timed out.")

async def setup(bot):
    await bot.add_cog(PlayersCog(bot))
