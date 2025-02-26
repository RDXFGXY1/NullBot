import discord
from discord.ext import commands
from discord.ui import Select, View
from googletrans import Translator
import os


# File paths for different texts
about_us_path = 'cogs/moderators/ServerInfo/about_us/about_us_en.txt'
rules_path = 'cogs/moderators/ServerInfo/about_us/rules_en.txt'
goals_path = 'cogs/moderators/ServerInfo/about_us/goals_en.txt'
terms_path = 'cogs/moderators/ServerInfo/about_us/terms_en.txt'



class LanguageSelect(Select):
    def __init__(self, bot):
        self.bot = bot
        options = [
            discord.SelectOption(
                label="Arabic | العربية",
                description="احصل على الدعم باللغة العربية",
                emoji="✔"
            ),
            discord.SelectOption(
                label="English | الانجليزية",
                description="Get support in English",
                emoji="✔"
            ),
            discord.SelectOption(
                label="Russian | الروسية",
                description="Получите поддержку на арабском языке",
                emoji="✔"
            ),
            discord.SelectOption(
                label="Darija | الدارجة المغربية",
                description="Get support in Moroccan Arabic",
                emoji="✔"
            )
        ]
        super().__init__(
            placeholder="Select Language | اختر اللغة",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        lang = self.values[0]
        print(lang)

        # Read the about_us text
        with open(about_us_path, 'r', encoding='utf-8') as f:
            about_us_text = f.read()

        # Translate and send message based on the selected language
        if lang == "Arabic | العربية":
            about_us_translated_text = self.translate_text(about_us_text, 'ar')
            if about_us_translated_text:
                await interaction.response.send_message(about_us_translated_text, ephemeral=True)
            else:
                await interaction.response.send_message("Sorry, translation failed.", ephemeral=True)

        elif lang == "English | الانجليزية":
            await interaction.response.send_message(about_us_text, ephemeral=True)

        elif lang == "Russian | الروسية":
            about_us_translated_text = self.translate_text(about_us_text, 'ru')
            if about_us_translated_text:
                await interaction.response.send_message(about_us_translated_text, ephemeral=True)
            else:
                await interaction.response.send_message("Sorry, translation failed.", ephemeral=True)

        elif lang == "Darija | الدارجة المغربية":
            await interaction.response.send_message("Not Available Yet", ephemeral=True)

    def translate_text(self, text, target_lang):
        try:
            translator = Translator()
            translated_text = translator.translate(text, dest=target_lang).text
            return translated_text
        except Exception as e:
            print(f"Error: {e}")
            return None


class AskLanguage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def create_language_view(self):
        # Create the view and add the LanguageSelect dropdown
        view = View(timeout=None)
        view.add_item(LanguageSelect(self.bot))
        return view


async def setup(bot):
    await bot.add_cog(AskLanguage(bot))
