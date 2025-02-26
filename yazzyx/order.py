# Yassin
# Yassin
# Yassin

import discord
from discord.ext import commands
from discord.ui import View, Select, Button
import json
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()


class OrderApplyAz(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="order_az", aliases=["az"])
    @commands.has_role(int(os.getenv("ADMIN_ROLE_ID")))  # Adjust with the correct role ID
    async def order_apply_az(self, ctx):
        if not ctx.guild.me.guild_permissions.send_messages:
            await ctx.send("<a:404:1311805750695428158> I need permission to send messages in this channel.")
            return

        view = OrderDropdownView(self.bot)
        embed = discord.Embed(
            title="🌟 Designe Ordering System 🌟",
            description="Choose the plane you want to order from the dropdown below 👇.",
            color=discord.Color.blue()
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/1312098797601689640/1313615270321066095/line_server.png?ex=6750c70e&is=674f758e&hm=959d8d94ee21d33636657f2cbbe329121c478148ab911f92a90836aabedfb92e&")
        await ctx.send(embed=embed, view=view)


class OrderDropdown(Select):
    def __init__(self, bot):
        self.bot = bot
        options = [
            discord.SelectOption(
                label="Order Design",
                description="Order a custom design",
                emoji="<a:basic:1311802809967968278>"
            ),
            discord.SelectOption(
                label="Packages",
                description="Order a package",
                emoji="<a:advanced:1311802803462737992>"
            ),
            discord.SelectOption(
                label="Other",
                description="Other designs or services you can order",
                emoji="📄"
            )
        ]

        super().__init__(
            placeholder="Select the type of order...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        bot_choice = self.values[0]
        emojis = {
            "Order Design": "<a:basic:1311802809967968278>",
            "Packages": "<a:advanced:1311802803462737992>",
            "Other": "📄"
        }

        emoji_plan = emojis.get(bot_choice)
        if not emoji_plan:
            await interaction.response.send_message(
                "Invalid choice. Please try again later.",
                ephemeral=True
            )
            return

        await self.ask_order_details(interaction, bot_choice, emoji_plan)

    async def ask_order_details(self, interaction: discord.Interaction, bot_choice: str, emoji_plan):
        try:
            await interaction.response.defer(ephemeral=True)
            user = interaction.user

            try:
                dm_channel = await user.create_dm()
            except discord.errors.Forbidden:
                await interaction.followup.send(
                    "I cannot send you a DM. Please enable DMs or contact the admin.",
                    ephemeral=True
                )
                return

            questions = [
                f"You have selected the **{emoji_plan} {bot_choice}**.\nPlease provide your **email address** 📧\n>Type `cancel` to exit.",
                f"Please provide your **payment method** 💳",
                f"Please provide any **additional details** (optional) 🤔"
            ]

            answers = []
            for question in questions:
                await dm_channel.send(question)
                try:
                    msg = await self.bot.wait_for(
                        "message",
                        check=lambda m: m.author == user and m.channel == dm_channel,
                        timeout=60
                    )
                except asyncio.TimeoutError:
                    await dm_channel.send("You took too long to respond. Order canceled.")
                    return

                if msg.content.lower() == "cancel":
                    await dm_channel.send("Order Canceled.")
                    return
                answers.append(msg.content)

            order_data = {
                "emoji_plan": emoji_plan,
                "order_id": f"{user.id}_{bot_choice}".replace(" ", "_"),
                "user_id": user.id,
                "username": user.name,
                "order_type": bot_choice,
                "status": "Pending",
                "progress": 0,
                "delivery_days": None,
                "order_details": {
                    "email": answers[0],
                    "payment_method": answers[1],
                    "additional_info": answers[2]
                }
            }

            os.makedirs("orders/yassine/", exist_ok=True)
            order_file = f"orders/yassine/{user.id}_{bot_choice}.json".replace(" ", "_")
            order_id=f"{user.id}_{bot_choice}".replace(" ", "_")
            with open(order_file, "w") as f:
                json.dump(order_data, f, indent=4)

            user_embed = discord.Embed(
                title="Order Completed <a:completed:1311807203031646228>",
                description="Your order has been submitted! Revise your order before sending it to the Designer.",
                color=discord.Color.green()
            )
            user_embed.add_field(name="Order Type", value=f"`{emoji_plan} {bot_choice}`", inline=False)
            user_embed.add_field(name="Your Email", value=answers[0], inline=False)
            user_embed.add_field(name="Payment Method", value=answers[1], inline=False)
            user_embed.add_field(name="Additional Details", value=answers[2], inline=False)
            user_embed.set_footer(text=f"Order submitted by {user.name}")
            user_embed.set_thumbnail(url=user.avatar.url)

            view = OrderManagementView(self.bot, order_data, dm_channel)
            await dm_channel.send(embed=user_embed, view=view)

        except Exception as e:
            print(f"Error submitting order: {e}")
            await interaction.followup.send(
                "<a:error:1311805750695428158> An error occurred while submitting your order. Please try again later.",
                ephemeral=True
            )


class OrderManagementView(View):
    def __init__(self, bot, order_data, dm_channel):
        super().__init__(timeout=None)
        self.bot = bot
        self.order_data = order_data
        self.dm_channel = dm_channel

    @discord.ui.button(label="Edit Order", style=discord.ButtonStyle.blurple)
    async def edit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Re-enter your order details to update the order.", ephemeral=True)
        questions = [
            "Please provide your updated **email address** 📧\n>Type `cancel` to exit.",
            "Please provide your updated **payment method** 💳",
            "Please provide your updated **additional details** (optional) 🤔"
        ]

        answers = []
        for question in questions:
            await self.dm_channel.send(question)
            try:
                msg = await self.bot.wait_for(
                    "message",
                    check=lambda m: m.author == interaction.user and m.channel == self.dm_channel,
                    timeout=60
                )
            except asyncio.TimeoutError:
                await self.dm_channel.send("You took too long to respond. Order canceled.")
                return

            if msg.content.lower() == "cancel":
                await self.dm_channel.send("Order Canceled.")
                return
            answers.append(msg.content)

        self.order_data['order_details']['email'] = answers[0]
        self.order_data['order_details']['payment_method'] = answers[1]
        self.order_data['order_details']['additional_info'] = answers[2]

        order_file = f"yazzyx/orders/{self.order_data['user_id']}_{self.order_data['order_type']}.json".replace(" ", "_")
        with open(order_file, "w") as f:
            json.dump(self.order_data, f, indent=4)

        await self.dm_channel.send("Order details updated successfully!")

    @discord.ui.button(label="<a:done:1311807203031646228> Confirm Order", style=discord.ButtonStyle.green)
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        await interaction.response.defer()
        with open(f"orders/channelsId/{user.id}.json", "r") as f:
            user_ticket_data = json.load(f)
            user_ticket_channel_id = user_ticket_data["channel_id"]
        admin_channel_id = [user_ticket_channel_id,"1311796798569971782"]  # Replace with the admin channel ID
        admin_channel = self.bot.get_channel(int(admin_channel_id[1]))
        user_channel_ticketId = self.bot.get_channel(admin_channel_id[0])
        if not admin_channel:
            await self.dm_channel.send("Could not find the admin channel. Please contact the admin.")
            return

        embed = discord.Embed(
                title="Designe Order Received <a:completed:1311807203031646228>",
                description=f":loading1: A new designe order has been placed by {user.mention} ",
                color=discord.Color.green()
            )
        embed.add_field(name="Order Type", value=self.order_data['order_type'], inline=False)
        embed.add_field(name="Your Email", value=self.order_data['order_details']['email'], inline=False)
        embed.add_field(name="Payment Method", value=self.order_data['order_details']['payment_method'], inline=False)
        embed.add_field(name="Additional Details", value=self.order_data['order_details']['additional_info'], inline=False)
        embed.set_footer(text=f"Order submitted by {user.name}")
        embed.set_thumbnail(url=user.avatar.url)

        await admin_channel.send(embed=embed)
        await user_channel_ticketId.send(embed=embed)
        confirm_embed = discord.Embed(
                title="Order Submitted 🎉",
                description=f"<a:done:1311800893376827582> Your bot order has been successfully submitted. We will review it soon!`",
                color=discord.Color.green()
            )
        confirm_embed.add_field(name="How to track your order?", value=f"<a:what:1311806173359509634> This is you Order it to chek your order Progress!\nCommnad: `-trackorder {self.order_data['order_id']}`")
        await self.dm_channel.send(embed=confirm_embed)
        self.stop()


class OrderDropdownView(View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.add_item(OrderDropdown(bot))


async def setup(bot):
    await bot.add_cog(OrderApplyAz(bot))
