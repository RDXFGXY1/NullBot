import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# TODO : Load environment variables
load_dotenv()

class MessageEditLogger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = int(os.getenv("ALL_LOG", "0"))  #* Log channel ID from .env

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        # Ignore bot messages
        if before.author.bot:
            return

        # Ignore if the content wasn't actually edited
        if before.content == after.content:
            return

        # Fetch the log channel
        log_channel = discord.utils.get(before.guild.channels, id=self.log_channel_id)

        if log_channel is None:
            print(f"⚠️ Log channel with ID {self.log_channel_id} not found in the server!")
            return

        # Prepare an embed for logging
        embed = discord.Embed(
            title="✏️ Message Edited",
            color=discord.Color.blurple()
        )
        embed.add_field(name="**Author**", value=before.author.mention, inline=True)
        embed.add_field(name="**Channel**", value=before.channel.mention, inline=True)
        embed.add_field(name="**Before**", value=before.content or "*[No content]*", inline=False)
        embed.add_field(name="**After**", value=after.content or "*[No content]*", inline=False)
        embed.set_footer(text="Message Edit Logger")

        # Send the embed to the log channel
        await log_channel.send(embed=embed)

        # Optionally, notify the edited channel
        await after.channel.send(
            f"🔍 {before.author.mention}, we saw that you edited your message! 👀",
            delete_after=10
        )

# Cog setup
async def setup(bot):
    await bot.add_cog(MessageEditLogger(bot))
