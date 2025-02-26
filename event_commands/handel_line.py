import discord
from discord.ext import commands

class HandleLine(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="line", description="Handles a line command")
    async def line(self, interaction: discord.Interaction):
        await interaction.response.send_message("This is a line command.")

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.tree.sync()
async def setup(bot):
    await bot.add_cog(HandleLine(bot))
