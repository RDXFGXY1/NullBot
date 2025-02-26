import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MemberModerationLogger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = int(os.getenv("ALL_LOG", "0"))  # Log channel from .env

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Triggered when a member leaves the server, including kicks and timeouts."""
        log_channel = discord.utils.get(member.guild.channels, id=self.log_channel_id)
        if log_channel:
            # Fetch audit logs to check if the member was kicked
            async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
                if entry.target == member:
                    # Member was kicked
                    embed = discord.Embed(
                        title="🚫 Member Kicked!",
                        description=f"{member.mention} was kicked by {entry.user.mention}.",
                        color=discord.Color.red()
                    )
                    embed.add_field(name="Reason", value=entry.reason if entry.reason else "No reason provided.")
                    embed.set_footer(text=f"User ID: {member.id}")
                    embed.set_author(name=member.name, icon_url=member.avatar.url)
                    await log_channel.send(embed=embed)
                    return  # Stop here since we confirmed it was a kick

            # Check if the member was likely timed out
            if member.timed_out_until and member.timed_out_until > discord.utils.utcnow():
                embed = discord.Embed(
                    title="⏳ Member Timed Out!",
                    description=f"{member.mention} was timed out in the server.",
                    color=discord.Color.orange()
                )
                embed.add_field(name="Timeout Ends", value=member.timed_out_until.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
                embed.set_footer(text=f"User ID: {member.id}")
                embed.set_author(name=member.name, icon_url=member.avatar.url)
                await log_channel.send(embed=embed)
                return

            # If no kick or timeout found, assume the member left voluntarily
            embed = discord.Embed(
                title="👋 Member Left",
                description=f"{member.mention} has left the server.",
                color=discord.Color.yellow()
            )
            embed.set_footer(text=f"User ID: {member.id}")
            embed.set_author(name=member.name, icon_url=member.avatar.url)
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        """Triggered when a member is banned."""
        log_channel = discord.utils.get(guild.channels, id=self.log_channel_id)
        if log_channel:
            # Fetch the ban reason from audit logs
            async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
                if entry.target == user:
                    embed = discord.Embed(
                        title="🚨 Member Banned!",
                        description=f"{user.mention} was banned by {entry.user.mention}.",
                        color=discord.Color.dark_red()
                    )
                    embed.add_field(name="Reason", value=entry.reason if entry.reason else "No reason provided.")
                    embed.set_footer(text=f"User ID: {user.id}")
                    embed.set_author(name=user.name, icon_url=user.avatar.url)
                    await log_channel.send(embed=embed)
                    return

# Cog setup
async def setup(bot):
    await bot.add_cog(MemberModerationLogger(bot))
