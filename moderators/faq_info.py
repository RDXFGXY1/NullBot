import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from .DashBoard.DachBoradLib import LanguageSelect
from .DashBoard.ServerInfo import LanguageSelectInfo

load_dotenv()

class FAQ(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='faq')
    async def faq_command(self, ctx):
        """
        Display frequently asked questions for the server
        """
        language = await LanguageSelect.get_server_language(ctx.guild.id)
        faq_info = await LanguageSelectInfo.get_faq_info(language)
        
        embed = discord.Embed(title="Frequently Asked Questions", color=discord.Color.blue())
        for question, answer in faq_info.items():
            embed.add_field(name=question, value=answer, inline=False)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(FAQ(bot))
