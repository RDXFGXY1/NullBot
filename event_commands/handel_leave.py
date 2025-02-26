import discord
from discord.ext import commands
import os
import random
from dotenv import load_dotenv
from datetime import datetime, timezone

# Load environment variables
load_dotenv()

class MemberLeave(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.leave_channel_id = int(os.getenv("ALL_LOG", "0"))  # Channel ID for logs from .env  

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        # Send a leave message to the log channel as embed
        leave_channel = discord.utils.get(member.guild.channels, id=self.leave_channel_id)
        if leave_channel:
            # Get the last message from the member (if any)
            async for message in member.history(limit=1):  # Get the last message in the server
                last_message = message.content if message else "No messages found."
                break

            # Create the farewell embed
            leave_embed = discord.Embed(
                title="Goodbye! 👋",
                description=f"**{member.name}** has left **{member.guild.name}**.\n"
                            f"We will miss you! 😢",
                color=discord.Color.red()
            )
            leave_embed.add_field(name="Account Created", value=f"{member.created_at.strftime('%Y-%m-%d %H:%M:%S')}", inline=False)
            leave_embed.add_field(name="Time in Server", value=self.calculate_time_in_server(member.joined_at), inline=True)
            leave_embed.add_field(name="Last Message", value=last_message, inline=False)
            leave_embed.add_field(name="Bot Account", value="Yes" if member.bot else "No", inline=True)
            leave_embed.set_footer(text="Farewell, until next time!")
            leave_embed.set_author(name=member.name, icon_url=member.avatar.url)
            leave_embed.set_thumbnail(url=member.avatar.url)

            # Fun GIF or Image for the farewell
            farewell_gifs = [
                "https://media.giphy.com/media/l2JhpjWPccQhsAMfu/giphy.gif",  # Sad detective gif
                "https://media.giphy.com/media/26ufdipQqU2lhNA4g/giphy.gif",  # Sherlock Holmes cat
                "https://media.giphy.com/media/d2jjuAZzDSVLZ5kI/giphy.gif",  # Pikachu looking sad
                "https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif",  # Sad dog
            ]
            leave_embed.set_image(url=random.choice(farewell_gifs))  # Random fun farewell GIF

            # Send the farewell message to the leave channel
            await leave_channel.send(embed=leave_embed)

    
    def calculate_time_in_server(self, joined_at):
        # Make 'now' aware by attaching UTC timezone
        now = datetime.now(timezone.utc)
        
        # Calculate the time difference
        difference = now - joined_at
        years = difference.days // 365
        months = (difference.days % 365) // 30
        days = (difference.days % 365) % 30

        time_in_server = f"{years} years, {months} months, {days} days"
        return time_in_server

# Cog setup
async def setup(bot):
    await bot.add_cog(MemberLeave(bot))
