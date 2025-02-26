import discord
from discord.ext import commands
from discord.ui import View, Select
from dotenv import load_dotenv
import os
from ..kyros.order import OrderDropdown as KyrosDropdown
from ..yazzyx.order import OrderDropdown as YazzyxDropdown

load_dotenv()

class AskOrdkerView(View):
    def __init__(self, bot):
        super().__init__(timeout=420)
        self.bot = bot
        self.add_item(AskOrdkerDropdown(bot))

class AskOrdkerDropdown(Select):
    def __init__(self, bot):
        self.bot = bot
        options = [
            discord.SelectOption(
                label="Order Bot",
                description="Create a new order for a bot.",
                emoji="<a:basic:1311802809967968278>",
            ),
            discord.SelectOption(
                label="Order Design",
                description="Create a new order for a design.",
                emoji="<a:advanced:1311802803462737992>",
            ),
        ]
        super().__init__(
            placeholder="Select the Order Type...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        bot_choice = self.values[0]

        if bot_choice == "Order Bot":
            await interaction.response.defer(ephemeral=True)  # Mark interaction as acknowledged
            # Add KyrosDropdown to a View
            view = View()
            view.add_item(KyrosDropdown(self.bot))
            await interaction.followup.send(
                "Please choose a bot plan...", view=view, ephemeral=True
            )
        elif bot_choice == "Order Design":
            await interaction.response.defer(ephemeral=True)  # Mark interaction as acknowledged
            # Add YazzyxDropdown to a View
            view = View()
            view.add_item(YazzyxDropdown(self.bot))
            await interaction.followup.send(
                "Please choose a design plan...", view=view, ephemeral=True
            )
        else:
            await interaction.response.defer(ephemeral=True)  # Mark interaction as acknowledged
            await interaction.followup.send(
                "<a:error:1311805750695428158> This option is not available. Please try again later.",
                ephemeral=True,
            )


class AskOrderCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


async def setup(bot):
    await bot.add_cog(AskOrderCog(bot))
