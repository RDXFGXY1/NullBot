import discord
from discord.ext import commands
from discord.ui import View, Select
import json
import os
from dotenv import load_dotenv


load_dotenv()

class OrderApply(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="order_ky", aliases=["ky"], description="Open the bot ordering system")
    @commands.has_role(int(os.getenv("ADMIN_ROLE_ID")))
    async def order(self, ctx):
        # Ensure the bot can send messages
        if not ctx.guild.me.guild_permissions.send_messages:
            await ctx.send("I need permission to send messages in this channel.")
            return

        view = OrderDropdownView(self.bot)
        embed = discord.Embed(
            title="🌟 Bot Ordering System 🌟",
            description="Choose the bot you want to order from the dropdown below 👇.",
            color=discord.Color.blue()
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/1312098797601689640/1313615270321066095/line_server.png?ex=6750c70e&is=674f758e&hm=959d8d94ee21d33636657f2cbbe329121c478148ab911f92a90836aabedfb92e&")
        await ctx.send(embed=embed, view=view)

class OrderDropdownView(View):
    def __init__(self, bot):
        super().__init__(timeout=420)  # Keep active for the user to choose an option
        self.bot = bot
        self.add_item(OrderDropdown(self.bot))

class OrderDropdown(Select):
    def __init__(self, bot):
        self.bot = bot
        options = [
            discord.SelectOption(
                label="Basic Bot",
                description="💳| $10 Delivery Time: 1-2 days",
                emoji="<a:basic:1311802809967968278>"
            ),
            discord.SelectOption(
                label="Advanced Bot",
                description="💳| $20 Delivery Time: 2-4 days",
                emoji="<a:advanced:1311802803462737992>"
            ),
            discord.SelectOption(
                label="Premium Bot",
                description="💳| $30 Delivery Time: 5-7 days",
                emoji="<a:premium:1311802823700385883>"
            ),
            discord.SelectOption(
                label="Other",
                description="Other bots or services you can order",
                emoji="📄"
            )
        ]
        super().__init__(
            placeholder="Select the bot you want to order...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()  # Defer the response to prevent timeout

        bot_choice = self.values[0]
        
        # Use a list instead of a set
        delivery_days = [1, 2, 5]  # Delivery times corresponding to bot choices
        emojis = ["<a:basic:1311802809967968278>", "<a:advanced:1311802803462737992>", "<a:premium:1311802823700385883>"]
        try:
            delivery_time = delivery_days[["Basic Bot", "Advanced Bot", "Premium Bot", "Other"].index(bot_choice)]
            emoji_plan = emojis[["Basic Bot", "Advanced Bot", "Premium Bot", "Other"].index(bot_choice)]
        except ValueError:
            await interaction.response.send_message(
                "Invalid bot choice. Please try again later.",
                ephemeral=True
            )
            return

        if bot_choice in ["Basic Bot", "Advanced Bot", "Premium Bot", "Other"]:
            await self.ask_order_details(interaction, bot_choice, delivery_time, emoji_plan)
            await interaction.followup.send(f"<a:completed:1311807203031646228> Order created successfully! Check your DM.")
        else:
            await interaction.followup.send(
                "<a:error:1311805750695428158> This option is not available. Please try again later.",
                ephemeral=True
            )

    async def ask_order_details(self, interaction: discord.Interaction, bot_choice: str, delivery_days: int = None, emoji_plan: str = None):
        try:

            user = interaction.user
            dm_channel = await user.create_dm()

            questions = [
                f"You have selected the ** {emoji_plan} {bot_choice}** bot.\nPlease provide your **email address** 📧",
                f"Please provide your **payment method** (e.g., PayPal, Credit Card) 💳",
                f"Please provide any **additional details** (optional) for the **{bot_choice}** bot 🤔"
            ]

            answers = []

            for question in questions:
                await dm_channel.send(question)
                msg = await self.bot.wait_for(
                    "message", 
                    check=lambda m: m.author == user and m.channel == dm_channel, 
                    timeout=60
                )
                answers.append(msg.content)

            order_data = {
                "emoji_plan": emoji_plan,
                "order_id": f"{user.id}_{bot_choice}".replace(" ", "_"),
                "user_id": user.id,
                "username": user.name,
                "bot_type": bot_choice,
                "status": "Pending",  # New field for order status
                "progress": 0,       # New field for progress percentage
                "delivery_days": delivery_days,
                "order_details": {
                    "email": answers[0],
                    "payment_method": answers[1],
                    "additional_info": answers[2]
                }
            }

            # Ensure directory exists
            os.makedirs("orders/kyros", exist_ok=True)

            # Fix directory and file name creation
            order_file = f"orders/kyros/{user.id}_{bot_choice}.json".replace(" ", "_")
            order_id = f"{user.id}_{bot_choice}".replace(" ", "_")
            with open(order_file, "w") as f:
                json.dump(order_data, f, indent=4)

            user_embed = discord.Embed(
                title="Order Submitted 🎉",
                description=f"<a:done:1311800893376827582> Your bot order has been successfully submitted. We will review it soon!\nYour order ID: `{user.id}_{bot_choice}`",
                color=discord.Color.green()
            )
            user_embed.add_field(name="How to track your order?", value=f"<a:what:1311806173359509634> This is you Order it to chek your order Progress!\nCommnad: `-trackorder {order_id}`")
            await dm_channel.send(embed=user_embed)

            #? Get channel id's
            #* read json from 
            with open(f"orders/channelsId/{user.id}.json", "r") as f:
                user_ticket_data = json.load(f)
                user_ticket_channel_id = user_ticket_data["channel_id"]

            

            order_channel_id = [user_ticket_channel_id, "1311796798569971782"]  # Replace with your order channel ID
            order_channel = interaction.client.get_channel(int(order_channel_id[1]))
            user_ticket_channelId = interaction.client.get_channel(order_channel_id[0])

            order_embed = discord.Embed(
                title="🚀 New Bot Order Received",
                description=f"<a:loading1:1311800875412623431> A new bot order has been placed by {user.mention}!",
                color=discord.Color.green()
            )
            order_embed.add_field(name="Bot Type", value=f"{emoji_plan} {bot_choice}", inline=False)
            order_embed.add_field(name="Email", value=answers[0], inline=False)
            order_embed.add_field(name="Payment Method", value=answers[1], inline=False)
            order_embed.add_field(name="Additional Details", value=answers[2], inline=False)
            order_embed.set_footer(text=f"Order submitted by {user.name}")
            order_embed.set_thumbnail(url=user.avatar.url)

            if order_channel:
                await order_channel.send(embed=order_embed)
                await user_ticket_channelId.send(embeb=order_embed)

        except Exception as e:
            print(f"Error submitting order: {e}")
            await interaction.followup.send(
                "<a:error:1311805750695428158> An error occurred while submitting your order. Please try again later.",
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(OrderApply(bot))
