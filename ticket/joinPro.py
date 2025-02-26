import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import mysql.connector
from datetime import datetime, timedelta
import asyncio


load_dotenv()

# Database configuration
db_config = {
    'host': 'mysql.db.bot-hosting.net',
    'user': 'u161499_bryBurlBJW',
    'password': '^hHClJ0yypSwr^l94DwE=Px.',
    'database': 's161499_Logic'
}


class JoinPro(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.level1_role_id = int(os.getenv("LEVEL1_ROLE_ID"))
        self.level2_role_id = int(os.getenv("LEVEL2_ROLE_ID"))
        self.level3_role_id = int(os.getenv("LEVEL3_ROLE_ID"))
        self.join_pro_channel_id = int(os.getenv("JOIN_PRO_CHANNEL_ID"))
        self.pro_role_id = int(os.getenv("PRO_ROLE_ID"))
        self.pro_bot_role_id = int(os.getenv("PRO_BOT_ROLE_ID"))
        
        

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Check if the message is in the join pro channel
        if message.channel.id == self.join_pro_channel_id:
            # Handle 'joinpro' command
            if message.content.startswith("joinpro"):
                user = message.author
                if any(role.id == self.pro_role_id for role in user.roles):
                    await message.channel.send("You're already a valued Pro member! 🌟")
                else:
                    joinProEmbed = discord.Embed(
                        title="LogicDEV Pro Membership Levels",
                        description=(
                            "**Level 1 - Access to Exclusive Tools**\n"
                            "Unlock powerful development tools tailored for your success!\n"
                            "Price: 12.6M ProBot currency/month\nTo join, type: -c 821359142362284055 1\n\n"
                            "**Level 2 - Premium Code Library**\n"
                            "Gain access to our hand-picked, high-quality code collections!\n"
                            "Price: 25.2M ProBot currency/month\nTo join, type: -c 821359142362284055 25263158\n\n"
                            "**Level 3 - Ultimate Developer Package**\n"
                            "Complete access to tools and code library - your ultimate coding companion!\n"
                            "Price: 37.8M ProBot currency/month\nTo join, type: -c 821359142362284055 37894737"
                        ),
                        color=discord.Color.gold()
                    )
                    await message.channel.send(embed=joinProEmbed)

            # Handle payment command
            elif message.content.startswith("-c 821359142362284055"):
                try:
                    parts = message.content.split()
                    if len(parts) < 3:
                        await message.channel.send("Invalid command format. Please try again.")
                        return

                    price = parts[2]
                    valid_prices = {
                        "1": "Level 1 Developer Tools",
                        "25263158": "Level 2 Premium Code Library",
                        "37894737": "Level 3 Ultimate Developer Package"
                    }

                    if price in valid_prices:
                        await message.channel.send(f"You've chosen {valid_prices[price]}!\nPlease complete ProBot payment.")

                        # Wait for the captcha response from ProBot
                        def check_captcha(msg):
                            return (
                                msg.channel.id == self.join_pro_channel_id and
                                msg.author.id == self.pro_bot_role_id and
                                msg.attachments  # Check if there's an image (captcha)
                            )

                        await self.bot.wait_for('message', check=check_captcha)

                        # Wait for the user to respond with the captcha code
                        def check_user_response(msg):
                            return (
                                msg.channel.id == self.join_pro_channel_id and
                                msg.author == message.author  # Ensure it's the correct user responding
                            )

                        await self.bot.wait_for('message', check=check_user_response)

                        # Wait for the payment confirmation message from ProBot
                        def check_payment(msg):
                            return (
                                msg.channel.id == self.join_pro_channel_id and
                                msg.author.id == self.pro_bot_role_id and
                                ":moneybag:" in msg.content and
                                "has transferred" in msg.content and
                                "<@!821359142362284055>" in msg.content
                            )

                        msg = await self.bot.wait_for('message', check=check_payment)

                        # Safely extract user name and price
                        user_name = msg.content.split("|")[1].split(",")[0].strip() if "|" in msg.content else "Unknown User"
                        price_value = msg.content.split("`")[1].replace("$", "") if "`" in msg.content else price

                        # Find the user object based on the user_name (mention or user_id)
                        user = message.guild.get_member_named(user_name.replace("@", ""))

                        # Check if the user was found
                        if user:
                            # Database connection
                            conn = mysql.connector.connect(**db_config)
                            cursor = conn.cursor()

                            # Insert payment details into the database
                            insert_query = """
                            INSERT INTO payments (user_id, user_name, price, membership_level, payment_date, expiry_date, payment_status, payment_method, payment_id)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """
                            payment_data = (
                                user.id,  # Use the Discord user ID
                                user_name,
                                price_value,
                                valid_prices[price],  # Match the price to the membership level
                                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S'),  # Assuming a 30-day membership
                                "Paid",
                                "ProBot",
                                user.id  # The user ID of the one making the payment
                            )

                            cursor.execute(insert_query, payment_data)
                            conn.commit()
                            cursor.close()
                            conn.close()

                        # Map prices to corresponding roles
                        price_role_map = {
                            "1": self.level1_role_id,  # Level 1 role
                            "25263158": self.level2_role_id,  # Level 2 role
                            "37894737": self.level3_role_id   # Level 3 role
                        }

                        if user and price in price_role_map:
                            role = message.guild.get_role(price_role_map[price])
                            embed_bill = discord.Embed(
                                title="<a:completed:1311807203031646228> LogicDEV Membership Confirmation Bill",
                                description=(
                                    f"**Member:** {user.mention}\n"
                                    f"**Membership Level:** {valid_prices[price]}\n"
                                    f"**Price:** ${price_value} Credits\n"
                                    f"**Payment Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                                    f"**Expiry Date:** {(datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')}\n"
                                    f"**Payment Status:** Paid\n"
                                    f"**Payment Method:** ProBot\n"
                                    f"**Payment ID:** {user.id}\n"
                                )
                            )
                            await user.add_roles(role)
                            await message.channel.send(f"{user.mention} has been granted {valid_prices[price]}!")
                            await user.send(embed=embed_bill)

                    else:
                        await message.channel.send("Invalid price. Please try again.\n**You're not smart if you're looking for a loophole.**")
                        async for msg in message.channel.history(limit=2):
                            if msg.author.id == self.pro_bot_role_id:
                                await msg.delete()

                except Exception as e:
                    await message.channel.send(f"An error occurred: {e}")


async def setup(bot):
    await bot.add_cog(JoinPro(bot))
