import discord
from discord.ext import commands
import random
from enum import Enum

class ShotType(Enum):
    SMASH = {"power": 90, "stamina": 80, "accuracy": 60, "risk": 8}
    DROP = {"power": 30, "stamina": 30, "accuracy": 75, "risk": 2}
    CLEAR = {"power": 70, "stamina": 50, "accuracy": 70, "risk": 4}
    NET_SHOT = {"power": 20, "stamina": 40, "accuracy": 85, "risk": 5}
    DRIVE = {"power": 75, "stamina": 60, "accuracy": 65, "risk": 6}

class Court:
    """Represents badminton court positioning"""
    FRONT = "front"
    BACK = "back"
    MID = "mid"

class Player:
    def __init__(self, name, speed=70, smash_power=75, defense=70, agility=65):
        self.name = name
        self.speed = speed
        self.smash_power = smash_power
        self.defense = defense
        self.agility = agility
        self.stamina = 100
        self.position = Court.MID
        self.score = 0

    def lose_stamina(self, amount):
        self.stamina = max(0, self.stamina - amount)

    def recover_stamina(self, amount=10):
        self.stamina = min(100, self.stamina + amount)

class Team:
    def __init__(self, name, player1, player2):
        self.name = name
        self.player1 = player1
        self.player2 = player2
        self.score = 0

    def add_point(self):
        self.score += 1

    def reset_score(self):
        self.score = 0

class Match:
    def __init__(self, team1, team2, max_points=21):
        self.team1 = team1
        self.team2 = team2
        self.max_points = max_points
        self.current_server = team1
        self.rally_count = 0
        self.match_history = []
        self.winner = None

    def execute_rally(self, team, shot_type: ShotType):
        """
        Execute a rally in the match
        Returns: (rally_result, winner_of_rally, details)
        """
        shot_stats = shot_type.value
        attacker = team.player1 if random.choice([True, False]) else team.player2
        
        # Stamina check
        if attacker.stamina < shot_stats["stamina"]:
            return False, None, f"❌ Not enough stamina! {attacker.name} has {attacker.stamina} stamina"
        
        # Execute shot
        shot_success = self._calculate_shot_success(attacker, shot_stats)
        
        if shot_success:
            # Calculate opponent response
            opponent_team = self.team2 if team == self.team1 else self.team1
            response_success = self._calculate_defense(opponent_team, shot_stats)
            
            if response_success:
                # Rally continues - randomize winner
                winner_team = team if random.random() > 0.5 else opponent_team
            else:
                winner_team = team
        else:
            # Shot failed
            opponent_team = self.team2 if team == self.team1 else self.team1
            winner_team = opponent_team
        
        # Award point
        winner_team.add_point()
        attacker.lose_stamina(shot_stats["stamina"])
        
        # Recover stamina for other players
        self.team1.player1.recover_stamina()
        self.team1.player2.recover_stamina()
        self.team2.player1.recover_stamina()
        self.team2.player2.recover_stamina()
        
        self.rally_count += 1
        details = self._generate_rally_narrative(attacker, shot_type, winner_team)
        
        return True, winner_team, details

    def _calculate_shot_success(self, player, shot_stats):
        """Calculate if shot lands in court"""
        base_accuracy = shot_stats["accuracy"]
        player_skill = (player.agility + player.smash_power) / 2
        combined_accuracy = (base_accuracy + player_skill) / 2
        return random.random() * 100 < combined_accuracy

    def _calculate_defense(self, team, incoming_shot):
        """Calculate if defense can return the shot"""
        defender = team.player1 if random.choice([True, False]) else team.player2
        defense_ability = (defender.defense + defender.agility) / 2
        shot_difficulty = incoming_shot["risk"] * 15  # Risk to difficulty conversion
        success_chance = defense_ability - shot_difficulty
        return random.random() * 100 < success_chance

    def _generate_rally_narrative(self, player, shot_type, winner_team):
        """Generate match commentary"""
        emoji_map = {
            ShotType.SMASH: "💥",
            ShotType.DROP: "🪶",
            ShotType.CLEAR: "✨",
            ShotType.NET_SHOT: "🕸️",
            ShotType.DRIVE: "⚡"
        }
        emoji = emoji_map.get(shot_type, "🏸")
        
        narration = f"{emoji} {player.name} plays a {shot_type.name.lower()}! "
        narration += f"**{winner_team.name}** scores! ({winner_team.score}-{self.team2.score if winner_team == self.team1 else self.team1.score})"
        return narration

    def is_match_over(self):
        """Check if match is finished (win by 2)"""
        if self.team1.score >= self.max_points or self.team2.score >= self.max_points:
            # Check win by 2 at high scores
            if abs(self.team1.score - self.team2.score) >= 2:
                self.winner = self.team1 if self.team1.score > self.team2.score else self.team2
                return True
        return False

    def get_score_display(self):
        return f"**{self.team1.name}** {self.team1.score} - {self.team2.score} **{self.team2.name}**"

class MatchCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_matches = {}

    @commands.command(name="match")
    async def start_match(self, ctx, max_points: int = 21):
        """Start a badminton doubles match (11 or 21 points)"""
        
        # Validate point selection
        if max_points not in [11, 21]:
            embed = discord.Embed(
                title="❌ Invalid Point Limit",
                description="Please choose either **11** or **21** points",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Create teams with AI players
        player1 = Player("You", speed=75, smash_power=78, defense=72, agility=70)
        partner = Player("AI Partner", speed=70, smash_power=73, defense=75, agility=68)
        opponent1 = Player("Opponent 1", speed=72, smash_power=76, defense=70, agility=71)
        opponent2 = Player("Opponent 2", speed=68, smash_power=74, defense=73, agility=69)

        team_player = Team("Your Team", player1, partner)
        team_opponent = Team("Opponents", opponent1, opponent2)

        match = Match(team_player, team_opponent, max_points)
        self.active_matches[ctx.author.id] = match

        embed = discord.Embed(
            title="🏸 Badminton GURU - Doubles Match Started!",
            description=f"**First to {max_points} points wins** (win by 2)",
            color=discord.Color.cyan()
        )
        embed.add_field(name="Your Team", value=f"{player1.name} & {partner.name}", inline=False)
        embed.add_field(name="Opponents", value=f"{opponent1.name} & {opponent2.name}", inline=False)
        embed.add_field(name="Score", value=match.get_score_display(), inline=False)
        embed.set_footer(text="Use bd shot <type> to play | Types: smash, drop, clear, net, drive")

        await ctx.send(embed=embed)

    @commands.command(name="shot")
    async def play_shot(self, ctx, shot_name: str = None):
        """Play a shot during an active match"""
        
        if ctx.author.id not in self.active_matches:
            await ctx.send("❌ You don't have an active match! Use `bd match` to start one.")
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

        embed = discord.Embed(
            title="🏸 Rally Result",
            description=details,
            color=discord.Color.green() if winner == match.team1 else discord.Color.orange()
        )
        embed.add_field(name="Current Score", value=match.get_score_display(), inline=False)
        embed.add_field(name="Your Stamina", value=f"{match.team1.player1.stamina}%", inline=True)
        embed.add_field(name="Partner Stamina", value=f"{match.team1.player2.stamina}%", inline=True)

        await ctx.send(embed=embed)

        # Check if match is over
        if match.is_match_over():
            winner_embed = discord.Embed(
                title="🎉 Match Over!",
                description=f"**{match.winner.name}** wins {match.winner.score} - {match.team1.score if match.winner == match.team2 else match.team2.score}!",
                color=discord.Color.gold()
            )
            await ctx.send(embed=winner_embed)
            del self.active_matches[ctx.author.id]

async def setup(bot):
    await bot.add_cog(MatchCog(bot))
