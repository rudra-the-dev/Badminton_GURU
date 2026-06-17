import discord
from discord.ext import commands
import random
import asyncio
from datetime import datetime

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
            u1.id: [100, 100],  # Player 1, Player 2
            u2.id: [100, 100]
        }
        
        # Calculate Team Average OVR balances
        team1_ovr = sum(p['ovr'] for p in roster1) / 2
        team2_ovr = sum(p['ovr'] for p in roster2) / 2

        # Choose initial random server
        current_server = u1 if random.choice([True, False]) else u2
        current_receiver = u2 if current_server == u1 else u1

        await channel.send(f"🪙 Coin toss complete! **{current_server.name}** will serve first.")
        await asyncio.sleep(2)

        # Global Match Loop
        while True:
            # 1. Check for 7-0 shutout rule
            if scores[u1.id] == 7 and scores[u2.id] == 0:
                await channel.send(f"👑 **SHUTOUT!** Match ended early via dominant 7-0 victory!")
                break
            if scores[u2.id] == 7 and scores[u1.id] == 0:
                await channel.send(f"👑 **SHUTOUT!** Match ended early via dominant 7-0 victory!")
                break

            # 2. Check standard 15 points win ceiling condition
            if scores[u1.id] >= 15 or scores[u2.id] >= 15:
                break

            # --- SERVICE PHASE ---
            embed = discord.Embed(
                title="🏸 Service Phase",
                description=f"{current_server.mention}, select your opening service delivery strategy:",
                color=0x00ACC1
            )
            embed.add_field(name="Scoreboard", value=f"**{u1.name}**: {scores[u1.id]} pts\n**{u2.name}**: {scores[u2.id]} pts", inline=False)
            
            view = GameActionView(current_server)
            view.children[0].label = "High Service"
            view.children[1].label = "Low Service"
            view.remove_item(view.children[2]) # Remove button C for service phase
            
            msg = await channel.send(embed=embed, view=view)
            timed_out = await view.wait()
            await msg.delete()

            if timed_out or not view.chosen_action:
                await channel.send(f"❌ Match abandoned: {current_server.name} timed out during service.")
                return

            last_shot = view.chosen_action
            attacker = current_server
            defender = current_receiver

            # --- RALLY LOOP PHASE ---
            rally_active = True
            while rally_active:
                # Deduct small stamina point values gracefully per cycle
                active_idx = random.randint(0, 1)
                stamina[attacker.id][active_idx] = max(10, stamina[attacker.id][active_idx] - random.randint(2, 5))
                stamina_factor = stamina[attacker.id][active_idx] / 100.0

                embed = discord.Embed(
                    title="🏸 Rally Continuous Stream",
                    description=f"{defender.mention}, opponent executed a **{last_shot}**!\nChoose your counter stroke maneuver:",
                    color=0xFFA500
                )
                
                view = GameActionView(defender)
                view.children[0].label = "Smash It"
                view.children[1].label = "Raise It"
                view.children[2].label = "Drop It"
                
                msg = await channel.send(embed=embed, view=view)
                timed_out = await view.wait()
                await msg.delete()

                if timed_out or not view.chosen_action:
                    await channel.send(f"❌ Match abandoned: {defender.name} timed out during active play.")
                    return

                counter_move = view.chosen_action

                # --- SHOT SUCCESS CALCULATION ENGINE ---
                # Check your hard rule matrix first
                if last_shot == "High Service" and counter_move == "Raise It":
                    await channel.send(f"💥 {defender.name} tried to **Raise/Lift** a **High Service**! The shuttle goes way OUT!")
                    scores[attacker.id] += 1
                    current_server = attacker
                    current_receiver = defender
                    rally_active = False
                else:
                    # Run system probability calculations using small OVR advantages + stamina factors + random weights
                    att_ovr = team1_ovr if attacker == u1 else team2_ovr
                    def_ovr = team2_ovr if attacker == u1 else team1_ovr
                    
                    base_success = 78 # Default rate
                    if counter_move == "Smash It": base_success = 65 # High risk option
                    
                    # Compute dynamic metrics balance
                    chance = base_success + ((def_ovr - att_ovr) * 0.2) + (stamina_factor * 5)
                    
                    if random.randint(1, 100) > chance:
                        # Defender wins the sequence point via unreturned shot conversion
                        await channel.send(f"✨ Brilliant return shot placement! {defender.name} answers with a gorgeous **{counter_move}** scoring a point!")
                        scores[defender.id] += 1
                        current_server = defender
                        current_receiver = attacker
                        rally_active = False
                    else:
                        # Rally keeps going back and forth safely
                        await channel.send(f"🏸 {defender.name} cleanly counters with a fine **{counter_move}**! The rally continues...")
                        last_shot = counter_move
                        # Swap roles for next hit execution
                        attacker, defender = defender, attacker
                        await asyncio.sleep(1.5)

        # --- MATCH RESOLUTION & DATABASE PROCESSING ---
        winner = u1 if scores[u1.id] > scores[u2.id] else u2
        loser = u2 if winner == u1 else u1

        embed = discord.Embed(
            title="🏁 Match Concluded!",
            description=f"🏆 **{winner.mention}** has won the match tournament!",
            color=0xFFD700
        )
        embed.add_field(name="Final Scores", value=f"**{u1.name}**: {scores[u1.id]} pts\n**{u2.name}**: {scores[u2.id]} pts", inline=False)
        
        # Payout Calculations
        w_coins, w_sp = 350, 25
        l_coins, l_sp = 120, 8
        
        embed.add_field(name=f"🥇 {winner.name} Rewards", value=f"+💰 {w_coins} Coins\n+⭐ {w_sp} Skill Points")
        embed.add_field(name=f"🥈 {loser.name} Rewards", value=f"+💰 {l_coins} Coins\n+⭐ {l_sp} Skill Points")
        await channel.send(embed=embed)

        # Save updates to database synchronously
        await self.bot.db.players.update_one({"user_id": winner.id}, {
            "$inc": {"coins": w_coins, "rank_points": 30, "wins": 1, "matches_played": 1}
        })
        await self.bot.db.players.update_one({"user_id": loser.id}, {
            "$inc": {"coins": l_coins, "rank_points": max(0, -10), "losses": 1, "matches_played": 1}
        })

async def setup(bot):
    await bot.add_cog(MatchEngineCog(bot))
              
