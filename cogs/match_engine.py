import discord
from discord.ext import commands
import random
import asyncio

class GameActionView(discord.ui.View):
    """Handles inputs for both service setups and counter strokes"""
    def __init__(self, allowed_user):
        super().__init__(timeout=60.0)
        self.allowed_user = allowed_user
        self.chosen_action = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.allowed_user.id:
            await interaction.response.send_message("❌ This is not your turn to play a shot!", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Action A", custom_id="btn_a", style=discord.ButtonStyle.primary)
    async def action_a(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.chosen_action = button.label
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="Action B", custom_id="btn_b", style=discord.ButtonStyle.secondary)
    async def action_b(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.chosen_action = button.label
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="Action C", custom_id="btn_c", style=discord.ButtonStyle.danger)
    async def action_c(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.chosen_action = button.label
        self.stop()
        await interaction.response.defer()


class MatchEngineCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def run_match_engine(self, channel, u1, roster1, u2, roster2):
        """Runs the main turn-based tactical simulation loop"""
        scores = {u1.id: 0, u2.id: 0}
        stamina = {
            u1.id: [100, 100],
            u2.id: [100, 100]
        }
        
        team1_ovr = sum(p['ovr'] for p in roster1) / 2
        team2_ovr = sum(p['ovr'] for p in roster2) / 2

        current_server = u1 if random.choice([True, False]) else u2
        current_receiver = u2 if current_server == u1 else u1

        await channel.send(f"🪙 Coin toss complete! **{current_server.name}** will serve first.")
        await asyncio.sleep(1.5)

        # Diverse list of dynamic continuation commentary text strings
        rally_commentary = [
            "🏸 {defender} lunges forward with a lightning-fast reflex cross-court save!",
            "🏸 {defender} intercepts with a crisp backhand block at the tape!",
            "🏸 {defender} tracks back perfectly, meeting the flight path cleanly.",
            "🏸 A beautiful diving recovery by {defender} to keep the rally alive!",
            "🏸 {defender} stands firm, firing back a flat, rapid mid-court drive.",
            "🏸 {defender} reads the flight path early and answers with a tight spinning touch."
        ]

        # Global Match Loop
        while True:
            # 1. Shutout check
            if (scores[u1.id] == 7 and scores[u2.id] == 0) or (scores[u2.id] == 7 and scores[u1.id] == 0):
                await channel.send(f"👑 **SHUTOUT!** Match ended early via dominant 7-0 victory!")
                break

            # 2. Win ceiling condition
            if scores[u1.id] >= 15 or scores[u2.id] >= 15:
                break

            # --- SERVICE PHASE ---
            embed = discord.Embed(
                title="🏸 Service Phase",
                description=f"{current_server.mention}, select your opening service delivery:",
                color=0x00ACC1
            )
            embed.add_field(name="Scoreboard", value=f"**{u1.name}**: `{scores[u1.id]}` pts\n**{u2.name}**: `{scores[u2.id]}` pts", inline=False)
            
            view = GameActionView(current_server)
            view.children[0].label = "High Service"
            view.children[1].label = "Low Service"
            view.remove_item(view.children[2]) 
            
            msg = await channel.send(embed=embed, view=view)
            timed_out = await view.wait()
            await msg.delete()

            if timed_out or not view.chosen_action:
                await channel.send(f"❌ Match abandoned: {current_server.name} timed out.")
                return

            last_shot = view.chosen_action
            attacker = current_server
            defender = current_receiver

            # --- RALLY LOOP PHASE ---
            rally_active = True
            while rally_active:
                # Deduct stamina smoothly per cycle
                active_idx = random.randint(0, 1)
                stamina_drain = random.randint(4, 8) if last_shot == "Smash It" else random.randint(2, 5)
                stamina[attacker.id][active_idx] = max(10, stamina[attacker.id][active_idx] - stamina_drain)
                stamina_factor = stamina[attacker.id][active_idx] / 100.0

                embed = discord.Embed(
                    title="🏸 Active Rally",
                    description=f"{defender.mention}, incoming shot: **{last_shot}**!\nChoose your counter strategy:",
                    color=0xFFA500
                )
                
                view = GameActionView(defender)
                view.children[0].label = "Smash It"   # Attacking Choice
                view.children[1].label = "Raise It"   # Defensive Choice
                view.children[2].label = "Drop It"    # Tactical Placement Choice
                
                msg = await channel.send(embed=embed, view=view)
                timed_out = await view.wait()
                await msg.delete()

                if timed_out or not view.chosen_action:
                    await channel.send(f"❌ Match abandoned: {defender.name} timed out.")
                    return

                counter_move = view.chosen_action

                # --- SHOT SUCCESS CALCULATION ENGINE ---
                # Hard Rule Clause
                if last_shot == "High Service" and counter_move == "Raise It":
                    await channel.send(f"💥 Out! {defender.name} tried to **Raise** a deep **High Service**! The shuttle flies completely out of bounds!")
                    scores[attacker.id] += 1
                    current_server = attacker
                    current_receiver = defender
                    rally_active = False
                else:
                    # Dynamic tactical success percentages based on choices
                    att_ovr = team1_ovr if attacker == u1 else team2_ovr
                    def_ovr = team2_ovr if attacker == u1 else team1_ovr
                    
                    # Balanced baseline survival rate (Lowered to speed up matches significantly)
                    base_survival = 52 
                    
                    # Tactical choice modifier injection
                    if counter_move == "Smash It":
                        base_survival -= 10  # Harder to execute successfully, high risk
                    elif counter_move == "Raise It":
                        base_survival += 12  # Safer return, keeps play alive easily
                        stamina[defender.id][random.randint(0,1)] = min(100, stamina[defender.id][random.randint(0,1)] + 3) # Small recovery
                    elif counter_move == "Drop It" and last_shot == "Smash It":
                        base_survival -= 5   # Hard counter drop under heavy pressure
                    
                    # OVR and Stamina adjustments
                    chance = base_survival + ((def_ovr - att_ovr) * 0.25) + (stamina_factor * 8)
                    chance = max(15, min(chance, 85)) # Keep bounds competitive

                    if random.randint(1, 100) > chance:
                        # Defensive side fails or offensive side kills the play sequence
                        if counter_move == "Smash It":
                            await channel.send(f"🔥 **BOOM!** An unstoppable steep smash from {defender.name} crashes onto the court floor! Point scored!")
                        elif counter_move == "Drop It":
                            await channel.send(f"✨ Precision play! {defender.name} feathers a stunning drop shot completely out of reach!")
                        else:
                            await channel.send(f"❌ Unforced error! {defender.name} misjudges the flight line and clips the net tape!")
                        
                        scores[defender.id] += 1
                        current_server = defender
                        current_receiver = attacker
                        rally_active = False
                    else:
                        # Rally successfully continues with unique randomized narrative commentary text string
                        chosen_text = random.choice(rally_commentary).format(defender=defender.name)
                        await channel.send(f"{chosen_text} * Countered with a clean **{counter_move}**!*")
                        last_shot = counter_move
                        attacker, defender = defender, attacker
                        await asyncio.sleep(1.2)

        # --- MATCH RESOLUTION & DATABASE PROCESSING ---
        winner = u1 if scores[u1.id] > scores[u2.id] else u2
        loser = u2 if winner == u1 else u1

        embed = discord.Embed(
            title="🏁 Match Concluded!",
            description=f"🏆 **{winner.mention}** has won the match tournament!",
            color=0xFFD700
        )
        embed.add_field(name="Final Scores", value=f"**{u1.name}**: `{scores[u1.id]}` pts\n**{u2.name}**: `{scores[u2.id]}` pts", inline=False)
        
        w_coins, w_sp = 350, 25
        l_coins, l_sp = 120, 8
        
        embed.add_field(name=f"🥇 {winner.name} Rewards", value=f"+💰 {w_coins} Coins\n+⭐ {w_sp} SP")
        embed.add_field(name=f"🥈 {loser.name} Rewards", value=f"+💰 {l_coins} Coins\n+⭐ {l_sp} SP")
        await channel.send(embed=embed)

        await self.bot.db.players.update_one({"user_id": winner.id}, {
            "$inc": {"coins": w_coins, "rank_points": 30, "wins": 1, "matches_played": 1}
        })
        await self.bot.db.players.update_one({"user_id": loser.id}, {
            "$inc": {"coins": l_coins, "rank_points": max(0, -10), "losses": 1, "matches_played": 1}
        })

async def setup(bot):
    await bot.add_cog(MatchEngineCog(bot))
