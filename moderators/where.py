import discord
from discord.ext import commands

class MemberLocation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="whereare", aliases=["whereis", "locate"], description="Shows the voice channel a member is in.")
    async def whereare(self, ctx, member: discord.Member):
        if member.voice and member.voice.channel:
            embed = discord.Embed(title="Member Location", description=f"{member.mention} is in **{member.voice.channel.name}**.", color=discord.Color.green())
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Member Location", description=f"{member.mention} is not connected to a voice channel.", color=discord.Color.red())
            await ctx.send(embed=embed)

    @whereare.error
    async def whereare_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(title="Error", description="Please specify a member.", color=discord.Color.red())
            await ctx.send(embed=embed)
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(title="Error", description="Could not find that member.", color=discord.Color.red())
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(MemberLocation(bot))
