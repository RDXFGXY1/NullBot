import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class MessageDeleteLogger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return  # Ignore bot messages

        # Fetch the log channel using the ID from .env file
        log_channel = discord.utils.get(message.guild.channels, id=int(os.getenv("ALL_LOG", "0")))
        if log_channel is None:
            print(f"⚠️ Log channel with ID {os.getenv('ALL_LOG', '0')} not found in the server!")
            return  # Log channel doesn't exist

        # Prepare a funny embed
        embed = discord.Embed(
            title="🕵️‍♂️ Message Deleted!",
            description=f"**Author:** {message.author.mention}\n"
                        f"**Channel:** {message.channel.mention}\n"
                        f"**Message:** `{message.content}`",
            color=discord.Color.orange()
        )
        embed.set_footer(text="Caught red-handed, or was it an innocent mistake?")

        #? Send the embed to the log channel
        await log_channel.send(embed=embed)

# Cog setup
async def setup(bot):
    await bot.add_cog(MessageDeleteLogger(bot))
