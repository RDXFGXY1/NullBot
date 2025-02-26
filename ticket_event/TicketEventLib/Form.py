import discord
from discord.ui import View, Button, TextInput, Modal
from discord.ext import commands
import os
from dotenv import load_dotenv as Load
import mysql.connector
import asyncio

Load()

# MySQL Database connection
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

class AdInputModal(Modal):
    def __init__(self, bot, title="Ad Input"):
        super().__init__(title=title)
        self.bot = bot  # Store the bot instance
        self.ads_channel_id = int(os.getenv("ADS_CHANNEL_ID"))
        
        self.add_item(TextInput(
            label="Ad Description",
            style=discord.TextStyle.paragraph,
            placeholder="Provide details about your ad...",
            required=True,
            max_length=1000
        ))
        
        self.add_item(TextInput(
            label="Server URL",
            style=discord.TextStyle.short,
            placeholder="Enter the server URL for the ad...",
            required=True,
            max_length=100
        ))

        self.add_item(TextInput(
            label="Ad Type",
            style=discord.TextStyle.short,
            placeholder="Enter the type of ad (e.g., @everyone, @here, Channel.)",
            required=True,
            max_length=50
        ))

        self.add_item(TextInput(
            label="Server Name",
            style=discord.TextStyle.short,
            placeholder="Enter the name of the server...",
            required=True,
            max_length=100
        ))

        self.add_item(TextInput(
            label="Ad Image URL",
            style=discord.TextStyle.short,
            placeholder="Enter the URL of the ad image (optional)",
            required=False,
            max_length=200
        ))

    async def on_submit(self, interaction: discord.Interaction):
        ad_description = self.children[0].value
        server_url = self.children[1].value
        ad_type = self.children[2].value
        server_name = self.children[3].value
        ad_image_url = self.children[4].value

        # Define ad pricing based on ad type
        ad_prices = {
            "@here": "7368422",
            "@everyone": "13684211",
            "Channel": "20000001"
        }

        # Check for valid ad type
        if ad_type not in ad_prices:
            await interaction.response.send_message("Invalid ad type. Please choose @here, @everyone, or Channel.", ephemeral=True)
            return

        # Inform the user to proceed with the payment command
        await interaction.response.send_message(
            f"To proceed with your ad, please send the following command in this channel:\n"
            f"`-c {os.getenv('BANK_ACC_ID')} {ad_prices[ad_type]}`\n"
            f"Then solve the CAPTCHA and complete the payment verification.",
            ephemeral=True
        )

        def check_captcha(msg):
            return (
                msg.channel.id == interaction.channel.id and
                msg.author.id == interaction.user.id and
                msg.content.isdigit()
            )

        def check_payment(msg):
            return (
                msg.channel.id == interaction.channel.id and
                msg.author.bot and
                ":moneybag:" in msg.content and
                "has transferred" in msg.content and
                "$" in msg.content and
                str(os.getenv("BANK_ACC_ID")) in msg.content
            )

        try:
            await self.bot.wait_for("message", check=check_captcha, timeout=300)
            msg = await self.bot.wait_for("message", check=check_payment, timeout=300)

            payment_message = msg.content
            user_name = payment_message.split('|')[0].split(',')[0].strip()
            price = payment_message.split('$')[1].split()[0]

            await interaction.followup.send("Payment confirmed! Your ad will be posted shortly.")

            db_connection = get_db_connection()
            cursor = db_connection.cursor()

            if ad_image_url is None:
                ad_image_url = "None"
            else:
                pass

            cursor.execute("""
                INSERT INTO ads (user_id, server_name, server_url, ad_type, ad_description, payment_id, ad_image_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                interaction.user.id,
                server_name,
                server_url,
                ad_type,
                ad_description,
                interaction.user.id,
                ad_image_url
            ))

            db_connection.commit()
            cursor.close()
            db_connection.close()

            #? Send the ad to the ads channel
            ads_channel = self.bot.get_channel(self.ads_channel_id)
            
            #? Create an embed for the ad
            embed = discord.Embed(
                title=f"Ad by {user_name}", 
                description=ad_description, 
                color=discord.Color.blue()
            )
            embed.add_field(name="Server", value=server_url, inline=False)
            if ad_image_url and ad_image_url != "None":
                embed.set_image(url=ad_image_url)
            
            #? Create view with buttons
            view = discord.ui.View()
            view.add_item(discord.ui.Button(label="Visit Server", style=discord.ButtonStyle.link, url=server_url))
            
            #? Send embed with buttons based on ad type
            if ad_type == "@here":
                await ads_channel.send(content="@here", embed=embed, view=view)
            elif ad_type == "@everyone":
                await ads_channel.send(content="@everyone", embed=embed, view=view)
            elif ad_type == "Channel":
                #? Create channel in the ads category
                category = discord.utils.get(interaction.guild.categories, id=int(os.getenv("ADS_CATEGORY_ID")))
                channel_name = f"ad-{server_name}"
                channel = await category.create_text_channel(channel_name)
                await channel.send("@everyone", embed=embed, view=view)

        except asyncio.TimeoutError:
            await interaction.followup.send("Payment verification timed out. Please try again.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"An error occurred: {str(e)}", ephemeral=True)


class AdButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Create Ad", style=discord.ButtonStyle.green)
    
    async def callback(self, interaction: discord.Interaction):
        modal = AdInputModal(self.view.bot)
        await interaction.response.send_modal(modal)

class AdView(View):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot  # Store the bot instance
        self.add_item(AdButton())


class AdForm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ad_button(self, ctx):
        """Send an ad creation button."""
        view = AdView(self.bot)  # Pass the bot instance to AdView
        await ctx.send("Click below to create an ad:", view=view)



async def setup(bot):
    await bot.add_cog(AdForm(bot))
