import discord
from discord.ext import commands
import json
import os
from datetime import datetime, timedelta

class StaffFeedback(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.staff_file = "config/staff/staff.json"
        self.cooldowns = {}  # Cooldown tracker for vouch and rep commands

        # Ensure the staff file exists
        if not os.path.exists(self.staff_file):
            os.makedirs(os.path.dirname(self.staff_file), exist_ok=True)
            with open(self.staff_file, "w") as f:
                json.dump({}, f)

    def load_staff_data(self):
        """Load staff data from the JSON file."""
        with open(self.staff_file, "r") as f:
            return json.load(f)

    def save_staff_data(self, data):
        """Save staff data to the JSON file."""
        with open(self.staff_file, "w") as f:
            json.dump(data, f, indent=4)

    def is_on_cooldown(self, user_id, command_name):
        """Check if a user is on cooldown for a command."""
        current_time = datetime.utcnow()
        if user_id in self.cooldowns:
            if command_name in self.cooldowns[user_id]:
                cooldown_time = self.cooldowns[user_id][command_name]
                if current_time < cooldown_time:
                    return cooldown_time - current_time
        return None

    def set_cooldown(self, user_id, command_name, cooldown_seconds):
        """Set a cooldown for a user and command."""
        current_time = datetime.utcnow()
        cooldown_time = current_time + timedelta(seconds=cooldown_seconds)
        if user_id not in self.cooldowns:
            self.cooldowns[user_id] = {}
        self.cooldowns[user_id][command_name] = cooldown_time

    @commands.command(name="vouch", help="Give a vouch to a staff member.")
    async def vouch(self, ctx, staff_member: discord.Member):
        """Command to vouch for a staff member."""
        user_id = ctx.author.id
        command_name = "vouch"

        # Check cooldown
        remaining_cooldown = self.is_on_cooldown(user_id, command_name)
        if remaining_cooldown:
            await ctx.send(
                f"You can use this command again in {remaining_cooldown.seconds} seconds.", delete_after=10
            )
            return

        # Load staff data
        staff_data = self.load_staff_data()
        if str(staff_member.id) not in staff_data:
            await ctx.send("The mentioned member is not a staff member.")
            return

        # Update vouches
        if "vouches" not in staff_data[str(staff_member.id)]:
            staff_data[str(staff_member.id)]["vouches"] = 0
        staff_data[str(staff_member.id)]["vouches"] += 1
        self.save_staff_data(staff_data)

        # Set cooldown
        self.set_cooldown(user_id, command_name, 86400)  # 24 hours in seconds

        await ctx.send(
            f"{ctx.author.mention} has vouched for {staff_member.mention}! They now have {staff_data[str(staff_member.id)]['vouches']} vouches."
        )

    @commands.command(name="rep", help="Give reputation to a staff member.")
    async def rep(self, ctx, staff_member: discord.Member):
        """Command to give reputation to a staff member."""
        user_id = ctx.author.id
        command_name = "rep"

        # Check cooldown
        remaining_cooldown = self.is_on_cooldown(user_id, command_name)
        if remaining_cooldown:
            await ctx.send(
                f"You can use this command again in {remaining_cooldown.seconds} seconds.", delete_after=10
            )
            return

        # Load staff data
        staff_data = self.load_staff_data()
        if str(staff_member.id) not in staff_data:
            await ctx.send("The mentioned member is not a staff member.")
            return

        # Update reputation
        if "reps" not in staff_data[str(staff_member.id)]:
            staff_data[str(staff_member.id)]["reps"] = 0
        staff_data[str(staff_member.id)]["reps"] += 1
        self.save_staff_data(staff_data)

        # Set cooldown
        self.set_cooldown(user_id, command_name, 86400)  # 24 hours in seconds

        await ctx.send(
            f"{ctx.author.mention} has given reputation to {staff_member.mention}! They now have {staff_data[str(staff_member.id)]['reps']} reputation points."
        )

    @commands.command(name="my_stats", help="Check your vouches and reputation points.")
    async def my_stats(self, ctx):
        """Command to check the vouches and reputation points of the user."""
        user_id = str(ctx.author.id)

        # Load staff data
        staff_data = self.load_staff_data()

        if user_id not in staff_data:
            await ctx.send(f"{ctx.author.mention}, you are not in the staff database.")
            return

        # Retrieve stats
        vouches = staff_data[user_id].get("vouches", 0)
        reps = staff_data[user_id].get("reps", 0)

        await ctx.send(
            f"{ctx.author.mention}, here are your stats:\n"
            f"📩 **Vouches**: {vouches}\n"
            f"🌟 **Reputation Points**: {reps}"
        )

async def setup(bot):
    await bot.add_cog(StaffFeedback(bot))
