import discord
from discord.ext import commands
import random
import asyncio

class MatchmakingView(discord.ui.View):
    """Initial button view to find a match opponent"""
    def __init__(self, bot, host_user):
        super().__init__(timeout=180.0)
        self.bot = bot
        self.host_user = host_user

    @discord.ui.button(label="Play", emoji="🏸", style=discord.ButtonStyle.green)
    async def join_match(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Rule Validation
        if interaction.user.id == self.host_user.id:
            await interaction.response.send_message("❌ You cannot play against yourself!", ephemeral=True)
            return

        # Fetch opponent profile from database
        opp_profile = await self.bot.db.players.find_one({"user_id": interaction.user.id})
        if not opp_profile:
            await interaction.response.send_message("❌ You need to create a profile first! Use `bdg start`.", ephemeral=True)
            return

        # Check inventory size rule
        if len(opp_profile.get("inventory", [])) < 2:
            await interaction.response.send_message("❌ You need at least 2 players in your roster to play a match! Use `bdg claim`.", ephemeral=True)
            return

        # Stop accepting inputs on this matchmaking request
        self.stop()
        
        # Advance layout view to player selection phase
        host_profile = await self.bot.db.players.find_one({"user_id": self.host_user.id})
        
        embed = discord.Embed(
            title="🏸 Match Accepted!",
            description=f"A match between **{self.host_user.mention}** and **{interaction.user.mention}** is preparing!",
            color=0x00ACC1
        )
        await interaction.response.edit_message(embed=embed, view=None)
        
        # Start sequential menu configurations
        cog = self.bot.get_cog("InteractiveMatchCog")
        await cog.start_roster_selection(interaction.channel, self.host_user, host_profile, interaction.user, opp_profile)

class RosterSelectMenu(discord.ui.Select):
    """Dropdown menu mapping owned players"""
    def __init__(self, placeholder_text, options_list):
        super().__init__(placeholder=placeholder_text, min_values=1, max_values=1, options=options_list)

    async def callback(self, interaction: discord.Interaction):
        self.view.selected_player = self.values[0]
        self.view.stop()

class RosterSelectionView(discord.ui.View):
    def __init__(self, allowed_user, placeholder, options_list):
        super().__init__(timeout=60.0)
        self.allowed_user = allowed_user
        self.selected_player = None
        self.add_item(RosterSelectMenu(placeholder, options_list))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.allowed_user.id:
            await interaction.response.send_message("❌ It is not your turn to choose players!", ephemeral=True)
            return False
        return True

class InteractiveMatchCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="match")
    async def host_match(self, ctx):
        """Look for a real opponent to play a 2v2 doubles match"""
        host_profile = await self.bot.db.players.find_one({"user_id": ctx.author.id})
        if not host_profile:
            await ctx.send("❌ Create your profile first! Use `bdg start` to register.")
            return

        if len(host_profile.get("inventory", [])) < 2:
            await ctx.send("❌ You need at least 2 players in your roster to play a match! Use `bdg claim`.")
            return

        embed = discord.Embed(
            title="🏸 Matchmaking",
            description=f"{ctx.author.mention} is looking for an opponent!",
            color=0x00ACC1
        )
        view = MatchmakingView(self.bot, ctx.author)
        await ctx.send(embed=embed, view=view)

    async def start_roster_selection(self, channel, user1, profile1, user2, profile2):
        """Drives sequential roster setup flow via drop-downs"""
        
        # ------------------ USER 1 SELECTION ------------------
        u1_p1 = await self.prompt_player_selection(channel, user1, profile1["inventory"], "Player 1 Selection", "Choose Player 1")
        if not u1_p1: return

        # Exclude selected player 1 from list
        u1_remaining = [p for p in profile1["inventory"] if p["name"] != u1_p1["name"]]
        u1_p2 = await self.prompt_player_selection(channel, user1, u1_remaining, "Player 2 Selection", "Choose Player 2 (Excluding Player 1)")
        if not u1_p2: return

        # ------------------ USER 2 SELECTION ------------------
        u2_p1 = await self.prompt_player_selection(channel, user2, profile2["inventory"], "Player 1 Selection", "Choose Player 1")
        if not u2_p1: return

        u2_remaining = [p for p in profile2["inventory"] if p["name"] != u2_p1["name"]]
        u2_p2 = await self.prompt_player_selection(channel, user2, u2_remaining, "Player 2 Selection", "Choose Player 2 (Excluding Player 1)")
        if not u2_p2: return

        # Package data and send to rally simulator execution engine
        await channel.send(f"✅ Roster configurations complete!\n**{user1.name}**: {u1_p1['name']} & {u1_p2['name']}\n**{user2.name}**: {u2_p1['name']} & {u2_p2['name']}\n\n*Initializing Match Engine Core...*")
        
        # Transitioning match loop hook
        match_engine = self.bot.get_cog("MatchEngineCog")
        if match_engine:
            self.bot.loop.create_task(match_engine.run_match_engine(channel, user1, [u1_p1, u1_p2], user2, [u2_p1, u2_p2]))

    async def prompt_player_selection(self, channel, user, inventory, heading, label):
        """Helper handler to build select boxes and return dictionary objects values"""
        options = []
        for idx, item in enumerate(inventory[:25]): # Discord limit 25 choices
            options.append(discord.SelectOption(
                label=f"{item['name']} (OVR: {item['ovr']})",
                value=item['name'],
                description=f"PWR: {item['smash_power']} | DEF: {item['defense']}"
            ))

        embed = discord.Embed(title=f"📋 {heading}", description=f"{user.mention}, choose your player selection below:", color=0x00ACC1)
        view = RosterSelectionView(user, label, options)
        msg = await channel.send(embed=embed, view=view)

        timed_out = await view.wait()
        if timed_out or not view.selected_player:
            await channel.send(f"❌ Match cancelled: {user.name} timed out during selection choices.")
            return None

        await msg.delete()
        # Find item object payload from name string
        return next(p for p in inventory if p["name"] == view.selected_player)

async def setup(bot):
    await bot.add_cog(InteractiveMatchCog(bot))
    
