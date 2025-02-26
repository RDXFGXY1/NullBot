import discord
from discord.ext import commands
import asyncio

class Moderation_Come(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="come", aliases=["Come"], description="Moves a member to your voice channel")
    @commands.has_permissions(move_members=True)
    async def come(self, ctx, member: discord.Member):
        if not ctx.guild.me.guild_permissions.move_members:
            await ctx.send("3tini permition a w9 ")
            return
        if not ctx.author.voice:
            await ctx.send("You are not connected to a voice channel.")
            return

        if not member.voice:
            await ctx.send(f"{member.mention} is not connected to a voice channel.")
            return

        try:
            await member.move_to(ctx.author.voice.channel)
            await ctx.send(f"{member.mention} has been moved to your voice channel.")
        except discord.Forbidden:
            await ctx.send("I do not have permission to move this member.")
        except Exception as e:
            await ctx.send(f"An unexpected error occurred: {e}")

    @come.error
    async def come_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specify a member to move.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("Could not find that member.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(f"You do not have permission to move members. {error}")

async def setup(bot):
    await bot.add_cog(Moderation_Come(bot))
