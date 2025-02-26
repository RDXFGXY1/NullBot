import discord
import re
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AutoModeration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.link_regex = r"(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})"
        self.ignored_channels = list(map(int, os.getenv("IGNORED_CHANNELS", "").split(", ")))  # Comma-separated channel IDs
        self.ignored_roles = list(map(int, os.getenv("IGNORED_ROLES", "").split(", ")))  # Comma-separated role IDs
        self.log_channel_id = int(os.getenv("ALL_LOG", "0"))  # Channel ID for logs (0 if unset)

    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            if message.author.bot:
                return  # Ignore bot messages

            # Ignore specific channels
            if message.channel.id in self.ignored_channels:
                return

            # Ignore users with specific roles
            if any(role.id in self.ignored_roles for role in message.author.roles):
                return

            # Check for links in the message
            links = re.findall(self.link_regex, message.content)
            if links:
                await message.delete()  # Delete the message

                # Notify the user
                embed = discord.Embed(
                    title="🚫 Link Not Allowed!",
                    description=f"{message.author.mention}, posting links is not allowed in this channel.",
                    color=discord.Color.red()
                )
                embed.set_footer(text="AutoModeration System")
                await message.channel.send(embed=embed, delete_after=10)

                # Log the action (if a log channel is set)
                if self.log_channel_id:
                    log_channel = self.bot.get_channel(self.log_channel_id)
                    if log_channel:
                        log_embed = discord.Embed(
                            title="🚨 Link Message Deleted",
                            description=f"**User:** {message.author.mention}\n"
                                        f"**Channel:** {message.channel.mention}\n"
                                        f"**Message:** {message.content}",
                            color=discord.Color.orange()
                        )
                        log_embed.set_footer(text="AutoModeration Log")
                        await log_channel.send(embed=log_embed)
        except Exception as e:
            print(f"Error in on_message: {e}")  # Log errors in the console

    # Command to add an ignored channel
    @commands.command(name="ignore_channel", description="Add a channel to the ignored list.")
    @commands.has_permissions(manage_channels=True)
    async def ignore_channel(self, ctx, channel: discord.TextChannel):
        if channel.id not in self.ignored_channels:
            self.ignored_channels.append(channel.id)
            await ctx.send(f"✅ {channel.mention} has been added to the ignored channels list.")
        else:
            await ctx.send(f"⚠️ {channel.mention} is already in the ignored channels list.")

    # Command to remove an ignored channel
    @commands.command(name="unignore_channel", description="Remove a channel from the ignored list.")
    @commands.has_permissions(manage_channels=True)
    async def unignore_channel(self, ctx, channel: discord.TextChannel):
        if channel.id in self.ignored_channels:
            self.ignored_channels.remove(channel.id)
            await ctx.send(f"✅ {channel.mention} has been removed from the ignored channels list.")
        else:
            await ctx.send(f"⚠️ {channel.mention} is not in the ignored channels list.")

    # Command to add an ignored role
    @commands.command(name="ignore_role", description="Add a role to the ignored list.")
    @commands.has_permissions(manage_roles=True)
    async def ignore_role(self, ctx, role: discord.Role):
        if role.id not in self.ignored_roles:
            self.ignored_roles.append(role.id)
            await ctx.send(f"✅ {role.mention} has been added to the ignored roles list.")
        else:
            await ctx.send(f"⚠️ {role.mention} is already in the ignored roles list.")

    # Command to remove an ignored role
    @commands.command(name="unignore_role", description="Remove a role from the ignored list.")
    @commands.has_permissions(manage_roles=True)
    async def unignore_role(self, ctx, role: discord.Role):
        if role.id in self.ignored_roles:
            self.ignored_roles.remove(role.id)
            await ctx.send(f"✅ {role.mention} has been removed from the ignored roles list.")
        else:
            await ctx.send(f"⚠️ {role.mention} is not in the ignored roles list.")

    # Command to set the log channel
    @commands.command(name="set_log_channel", description="Set the log channel for filtered messages.")
    @commands.has_permissions(manage_channels=True)
    async def set_log_channel(self, ctx, channel: discord.TextChannel):
        self.log_channel_id = channel.id
        await ctx.send(f"✅ Log channel has been set to {channel.mention}.")

# Cog setup
async def setup(bot):
    await bot.add_cog(AutoModeration(bot))
