import discord
from discord.ext import commands, tasks
import json
import os
import datetime
from dotenv import load_dotenv

load_dotenv()


class OrderManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_orders = {}  # For tracking progress of active orders

    # Command: Start an order
    @commands.command(name="begin", description="Start processing an order.")
    @commands.has_role(int(os.getenv("SELLER_ROLE_ID")))
    async def begin_order(self, ctx, order_id: str):
        try:
            order_file = f"orders/kyros/{order_id}.json"
            if not os.path.exists(order_file):
                await ctx.send("<a:404:1311805721654067280> Order not found. Please check the Order ID.")
                return

            with open(order_file, "r") as f:
                order_data = json.load(f)

            if order_data["status"] != "Pending":
                await ctx.send("<a:error:1311805750695428158> Order has already been started or completed.")
                return

            # Update the order status to "In Progress"
            order_data["status"] = "In Progress"
            order_data["start_time"] = str(datetime.datetime.now())

            with open(order_file, "w") as f:
                json.dump(order_data, f, indent=4)

            self.active_orders[order_id] = order_data
            await ctx.send(f"<a:completed:1311807203031646228> Order `{order_id}` has been started and is now in progress!")
        except Exception as e:
            await ctx.send(f"<a:error:1311805750695428158> An error occurred: {e}")

    # Command: Track an order
    @commands.command(name="trackorder", description="Track the progress of an order.")
    @commands.has_role(int(os.getenv("USER_ROLE_ID")))
    async def track_order(self, ctx, order_id: str):
        try:
            order_file = f"orders/kyros/{order_id}.json"
            if not os.path.exists(order_file):
                await ctx.send("<a:404:1311805721654067280> Order not found. Please check the Order ID.")
                return

            with open(order_file, "r") as f:
                order_data = json.load(f)

            # Calculate progress if the order is in progress
            progress = order_data.get("progress", 0)
            status = order_data["status"]

            if status == "In Progress":
                start_time = datetime.datetime.fromisoformat(order_data["start_time"])
                elapsed_time = (datetime.datetime.now() - start_time).total_seconds()  # Calculate in seconds
                delivery_days = int(order_data.get("delivery_days", 1))
                total_delivery_time = delivery_days * 24 * 60 * 60  # Convert delivery days to seconds
                progress = min(100, (elapsed_time / total_delivery_time) * 100)  # Fractional progress
                order_data["progress"] = progress

                # Update status automatically if completed
                if progress >= 100:
                    order_data["status"] = "Completed"
                    status = "Completed"

                # Save updated progress
                with open(order_file, "w") as f:
                    json.dump(order_data, f, indent=4)

            # Visual progress bar
            # Calculate the fraction of the progress bar filled
            filled_segments = int(progress / 10)
            progress_bar = "█" * filled_segments + "░" * (10 - filled_segments)

            # Format the progress as a precise percentage
            progress_percentage = f"{progress:.2f}%"

            # Create the embed with the progress bar
            embed = discord.Embed(
                title=f"Order Tracking: {order_id}",
                description=f"Status: {status}\nProgress: `{progress_percentage}`\n<a:Loading:1311800885654847509> [{progress_bar}]",
                color=discord.Color.blue()
            )

            # Send the embed
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"<a:error:1311805750695428158> An error occurred: {e}")

    # Command: Update an order
    @commands.command(name="updateorder", description="Update an order's status or delivery time.")
    @commands.has_role(int(os.getenv("ADMIN_ROLE_ID")))
    async def update_order(self, ctx, order_id: str, new_status: str, new_delivery_days: int = None):
        try:
            order_file = f"orders/kyros/{order_id}.json"
            if not os.path.exists(order_file):
                await ctx.send("<a:404:1311805721654067280> Order not found. Please check the Order ID.")
                return

            with open(order_file, "r") as f:
                order_data = json.load(f)

            # Update status
            order_data["status"] = new_status

            # Optionally update delivery time
            if new_delivery_days:
                order_data["delivery_days"] = new_delivery_days

            with open(order_file, "w") as f:
                json.dump(order_data, f, indent=4)

            await ctx.send(f"<a:completed:1311807203031646228> Order `{order_id}` has been updated: Status: `{new_status}`.")
        except Exception as e:
            await ctx.send(f"<a:error:1311805750695428158> An error occurred: {e}")

async def setup(bot):
    await bot.add_cog(OrderManagement(bot))
