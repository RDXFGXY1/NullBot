import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AutoRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.auto_role_id = int(os.getenv("USER_ROLE_ID"))  # Load the role ID from .env

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Fetch the role using the ID from .env
        role = discord.utils.get(member.guild.roles, id=self.auto_role_id)

        # Check if the role exists in the server
        if role is None:
            print(f"⚠️ Role with ID {self.auto_role_id} not found in the server!")
            return

        # Assign the role to the new member
        try:
            await member.add_roles(role)
            # send to memeber dm in embed
            dm_embed = discord.Embed(
                title="Welcome to the Server!",
                description=f"Hey {member.mention}, welcome to our server! 🎉 You've been automatically given the {role.name} role.  Enjoy your stay!",
                color=discord.Color.green()
            )
            await member.send(embed=dm_embed)
            print(f"✅ Assigned {role.name} to {member.display_name}")

        except Exception as e:
            print(f"⚠️ Failed to assign role: {e}")

# Cog setup
async def setup(bot):
    await bot.add_cog(AutoRole(bot))
