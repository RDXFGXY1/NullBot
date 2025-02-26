import discord
from discord.ext import commands
import json
import os
from dotenv import load_dotenv

# Load env file form root dir
load_dotenv()

class CheckOrdersAz(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="Acheck_orders", description="Check all submitted orders")
    @commands.has_permissions(administrator=True)
    async def check_orders(self, ctx):
        # Ensure the orders folder exists
        if not os.path.exists("orders"):
            await ctx.send("No orders found.")
            return

        orders = []
        for filename in os.listdir("orders/yassine"):
            if filename.endswith(".json"):
                filepath = os.path.join("orders/yassine", filename)
                with open(filepath, "r") as f:
                    try:
                        data = json.load(f)
                        orders.append(data)
                    except json.JSONDecodeError:
                        print(f"Error decoding JSON in file: {filepath}")

        if not orders:
            await ctx.send("No orders found.")
            return

        embed = discord.Embed(
            title="Orders Overview",
            description="Here's a summary of all submitted orders:",
            color=discord.Color.green()
        )

        for order in orders:
            user = self.bot.get_user(order["user_id"])
            username = user.name if user else order["username"]
            embed.add_field(
                name=f"Order by {username} ({order['user_id']})",
                value=f"**Bot Type:** {order['order_type']}\n**Order ID:** `{order['order_id']}`** \n**Status:** `{order['status']}`\n**Delivery Days:** `{order['delivery_days']}` days\n**Email:** `{order['order_details']['email']}`\n**Payment Method:** `{order['order_details']['payment_method']}`",
                inline=False
            )
        await ctx.send(embed=embed)

        # User Check Order command
    @commands.command(name="Acheck_my_order", description="Check your order status")
    @commands.check(lambda ctx: ctx.author.id)
    @commands.has_role(os.getenv("USER_ROLE_ID"))
    async def check_my_order(self, ctx):
        user_id = ctx.author.id
        found_order = False
        for filename in os.listdir("orders/yassine"):
            if filename.startswith(str(user_id)):
                filepath = os.path.join("orders/yassine", filename)
                with open(filepath, "r") as f:
                    try:
                        order_data = json.load(f)
                        embed = discord.Embed(
                            title=f"Your Order Status ({order_data['order_id']})",
                            description=f"**Bot Type:** {order_data['order_type']}\n**Status:** {order_data['status']}\n**Delivery Days:** {order_data['delivery_days']} days",
                            color=discord.Color.blue()
                        )
                        await ctx.send(embed=embed, ephemeral=True)
                        found_order = True
                        break  # Exit the loop after finding the order
                    except json.JSONDecodeError:
                        print(f"Error decoding JSON in file: {filepath}")
        if not found_order:
            await ctx.send("No order found for you.")


async def setup(bot):
    await bot.add_cog(CheckOrdersAz(bot))
