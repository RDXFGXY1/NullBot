import discord
from discord.ext import commands
import asyncio
import os
import json


class ApplyAction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="apply_action", description="Accept or Reject a staff application")
    @commands.has_permissions(administrator=True)  # Only allow admins to use this command
    async def apply_action(self, ctx, user_id: int, accept: str):
        # Check if accept is 'true' or 'false'
        if accept not in ["true", "false"]:
            await ctx.send("Invalid argument. Please use 'true' to accept or 'false' to reject the application.")
            return
        
        # Find the application file
        application_file = f"apply/{user_id}.json"
        
        if not os.path.exists(application_file):
            await ctx.send(f"No application found for user with ID {user_id}.")
            return
        
        # Load application data
        with open(application_file, "r") as file:
            application_data = json.load(file)
        
        # Fetch member object from the guild (not user)
        member = ctx.guild.get_member(user_id)
        if not member:
            await ctx.send(f"Member with ID {user_id} not found in this server.")
            return
        
        # Get the staff role by ID 
        staff_role_id = 1310585759702716447  
        staff_role = ctx.guild.get_role(staff_role_id)
        if not staff_role:
            await ctx.send("Staff role not found.")
            return
        
        # Accept or Reject
        if accept == "true":
            # Add the staff role to the user
            await member.add_roles(staff_role)
            await ctx.send(f"{member.name} has been accepted into the staff team!")

            # Notify the user of the acceptance
            dm_channel = await member.create_dm()
            accept_embed = discord.Embed(
                title="Staff Application Accepted 🎉",
                description="Congratulations! You have been accepted into the staff team. Welcome aboard!",
                color=discord.Color.green()
            )
            await dm_channel.send(embed=accept_embed)
        else:
            # Reject the application
            await ctx.send(f"{member.name} has been rejected for the staff team.")

            # Notify the user of the rejection
            dm_channel = await member.create_dm()
            reject_embed = discord.Embed(
                title="Staff Application Rejected ❌",
                description="Sorry, your application has been rejected. Better luck next time!",
                color=discord.Color.red()
            )
            await dm_channel.send(embed=reject_embed)

async def setup(bot):
    await bot.add_cog(ApplyAction(bot))