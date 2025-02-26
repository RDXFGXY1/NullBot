import discord 
from discord.ext import commands
from discord.ui import Select, View
from googletrans import Translator
import os
from ..DashBoard.DachBoradLib import rules_path, about_us_path, goals_path, terms_path, LanguageSelect


class LanguageSelectInfo(Select):
    def __init__(self):
        # Reading First line in rules_path, about_us_path, goals_path, terms_path
        options_list = []
        for path in [about_us_path, rules_path, goals_path, terms_path]:
            with open(path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                options_list.append(
                    discord.SelectOption(
                        label=first_line,
                        description=f"Read {first_line}",
                        emoji="📖"
                    )
                )
        super().__init__(
            placeholder="Select your language",
            min_values=1,
            max_values=1,
            options=options_list
        )

    async def callback(self, interaction: discord.Interaction):
        #? Check if fisrt line is Ture
        selected_option = self.values[0]
        for path, option in zip([about_us_path, rules_path, goals_path, terms_path], self.options):
            if option.label == selected_option:
                with open(path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                await interaction.response.send_message(file_content, ephemeral=True)
                break

class ServerInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def server_info(self):
        view=View(timeout=None)
        view.add_item(LanguageSelectInfo(self.bot))
        return view

async def setup(bot):
    await bot.add_cog(ServerInfo(bot))
