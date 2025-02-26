import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = int(os.getenv("ALL_LOG", "0"))  # Log channel ID from environment variable

    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context):
        """Triggered when a command is used."""
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            embed = discord.Embed(
                title="Command Used",
                description=f"**User:** {ctx.author} ID: {ctx.author.id}\n"
                            f"**Channel:** {ctx.channel} <#{ctx.channel.id}>\n"
                            f"**Command:** `-{ctx.command}`",
                color=discord.Color.orange(),
                timestamp=ctx.message.created_at
            )
            embed.set_footer(text=f"Guild: {ctx.guild.name} ({ctx.guild.id})")
            await log_channel.send(embed=embed)
        else:
            print(f"Log channel not found! Check if LOG_CHANNEL_ID is set correctly.")

# Add this cog to your bot
async def setup(bot):
    await bot.add_cog(Logging(bot))
