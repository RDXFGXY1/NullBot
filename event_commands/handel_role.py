import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class RoleUpdateLogger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = int(os.getenv("ALL_LOG", "0"))  # Channel to log updates

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        # Check if roles have changed
        if before.roles != after.roles:
            log_channel = discord.utils.get(after.guild.channels, id=self.log_channel_id)
            if log_channel:
                # Find the roles that were added and removed
                added_roles = [role for role in after.roles if role not in before.roles]
                removed_roles = [role for role in before.roles if role not in after.roles]

                # Create an embed for the log
                embed = discord.Embed(
                    title="Role Updated!",
                    description=f"{after.mention} has had their roles updated!",
                    color=discord.Color.blue()
                )
                embed.add_field(name="Added Roles", value=", ".join([role.name for role in added_roles]) if added_roles else "None", inline=False)
                embed.add_field(name="Removed Roles", value=", ".join([role.name for role in removed_roles]) if removed_roles else "None", inline=False)
                embed.set_footer(text=f"User ID: {after.id}")
                embed.set_author(name=after.name, icon_url=after.avatar.url)
                
                # Send the embed to the log channel
                await log_channel.send(embed=embed)

# Cog setup
async def setup(bot):
    await bot.add_cog(RoleUpdateLogger(bot))
