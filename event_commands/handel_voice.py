import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

#* LOAD ENV:S 
load_dotenv()

class VoiceChannelLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.LOG_CHANNEL = os.getenv("ALL_LOG")
        print(f"{self.LOG_CHANNEL}\t LOG CHANNEL --------------")  # Fixed typo here

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """
        Triggered whenever a member's voice state changes (join, leave, mute, etc.).
        """
        # Get the log channel
        logs_channel = discord.utils.get(member.guild.text_channels, id=int(self.LOG_CHANNEL))  # Ensure this is an integer
        if not logs_channel:
            return  # No logs channel found

        # Detect events
        embed = discord.Embed(title="Voice Channel Update", color=discord.Color.blue())
        embed.set_author(name=member.display_name, icon_url=member.avatar.url)

        if before.channel != after.channel:
            # Joined a channel
            if after.channel:
                embed.description = f"🔊 **Joined** `{after.channel.name}`"
            # Left a channel
            elif before.channel:
                embed.description = f"🔇 **Left** `{before.channel.name}`"

        if before.self_mute != after.self_mute:
            state = "Muted" if after.self_mute else "Unmuted"
            embed.add_field(name="Mute Status", value=f"🎙️ {state}", inline=False)

        if before.self_deaf != after.self_deaf:
            state = "Deafened" if after.self_deaf else "Undeafened"
            embed.add_field(name="Deafen Status", value=f"🔇 {state}", inline=False)

        if before.self_video != after.self_video:
            state = "Enabled" if after.self_video else "Disabled"
            embed.add_field(name="Video Status", value=f"📹 {state}", inline=False)

        if before.self_stream != after.self_stream:
            state = "Started" if after.self_stream else "Stopped"
            embed.add_field(name="Streaming Status", value=f"🎥 {state}", inline=False)

        # Send log to the logs channel
        if embed.description or embed.fields:
            await logs_channel.send(embed=embed)


# Add the cog to the bot
async def setup(bot):
    await bot.add_cog(VoiceChannelLogs(bot))
