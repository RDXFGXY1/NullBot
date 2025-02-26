
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import json
from .DashBoard.DachBoradLib import AskLanguage

load_dotenv()

class DashBoard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="dashborad", aliases=["dash"], description="Send dashboard")
    @commands.has_role(int(os.getenv("ADMIN_ROLE_ID")))
    async def dashborad(self, ctx):
        with open("config/staff/staff.json", "r") as f:
            staff_data = json.load(f)
        formatted_staff_list = ""
        for staff_id, info in staff_data.items():
            name = info["name"]
            formatted_staff_list += f"- <@{staff_id}> > {name}\n"

        dash_emdeb = discord.Embed(
            title=f"{ctx.guild.name} Dashboard",
            description=f"__Staff List__\n{formatted_staff_list}",
            color=discord.Color.blue()
        )
        dash_emdeb.add_field(name="Learn more **__about us__**", value="Get More Information About Us\n> **Including** :\n> - __Our Terms__\n> - __Our Rules__\n> - __Our Goals__", inline=False)
        dash_emdeb.add_field(name="تعرف على المزيد **__عنّا__**", value="احصل على مزيد من المعلومات عنّا\n> **بما في ذلك** :\n > - __شروطنا__\n> - __قواعدنا__\n> - __أهدافنا__", inline=False)
        dash_emdeb.set_image(url="https://cdn.discordapp.com/attachments/1312098797601689640/1317223330096611378/line.png?ex=675de752&is=675c95d2&hm=8ae12f73634b903d8a4b4b99344abe7bd9aa82f04be724c59a03fd97385ce212&")
        dash_emdeb.set_thumbnail(url=ctx.guild.icon.url)
        
        # Creating a view and adding the AskLanguage dropdown as an item
        ask_language_cog = self.bot.get_cog("AskLanguage")
        view = ask_language_cog.create_language_view()

        await ctx.send(embed=dash_emdeb, view=view)

async def setup(bot):
    await bot.add_cog(DashBoard(bot))