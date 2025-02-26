import discord
from discord.ext import commands
import asyncio
from dotenv import load_dotenv
import os

# Load env file from root dir
load_dotenv()

class FeedbackSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.feedback_channel_id = int(os.getenv("FEEDBACK_CHANNEL_ID"))  # Feedback channel ID from the .env file

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore messages from bots
        if message.author.bot:
            return

        # Check if the message is sent in the feedback channel
        if message.channel.id == self.feedback_channel_id:
            # Save the original message content
            feedback_message = message.content

            # Delete the user's original message
            await message.delete()

            # Create a styled embed for the feedback
            feedback_embed = discord.Embed(
                title="📢 User Feedback",
                description=f"**Message:**\n{feedback_message}",
                color=discord.Color.orange(),
                timestamp=message.created_at,
            )
            feedback_embed.set_author(
                name=f"{message.author.display_name} ({message.author.name}#{message.author.discriminator})",
                icon_url=str(message.author.avatar.url) if message.author.avatar else str(message.author.default_avatar),
            )
            feedback_embed.set_footer(
                text=f"User ID: {message.author.id}"
            )

            # Repost the message as an embed in the same channel
            feedback_message_embed = await message.channel.send(embed=feedback_embed)

            # Add voting reactions for members
            await feedback_message_embed.add_reaction("👍")
            await feedback_message_embed.add_reaction("👎")

            # Notify the user that their feedback has been successfully submitted
            try:
                await message.author.send(
                    embed=discord.Embed(
                        title="✅ Feedback Submitted",
                        description=f"Thank you for your feedback! Your message was successfully sent to {message.channel.mention}.",
                        color=discord.Color.green(),
                    )
                )
            except discord.Forbidden:
                # If the bot cannot DM the user
                
                pass

# Setup the cog
async def setup(bot):
    await bot.add_cog(FeedbackSystem(bot))
