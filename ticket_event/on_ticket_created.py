import discord
from discord.ext import commands
from discord.ui import View, Button, Select, TextInput, Modal
import os
from dotenv import load_dotenv
import mysql.connector
import asyncio
import re  # Importing regular expression module
from .TicketEventLib.Form import AdView

load_dotenv()

class TicketEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ticket_bot = int(os.getenv("TICKET_BOT_ID"))
        self.guild_id = int(os.getenv("GUILD_ID"))
        self.db_connection = self.get_db_connection()

    # Function to get a DB connection
    def get_db_connection(self):
        return mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        print(f"Channel created: {channel.name} in guild {channel.guild.name}")

        if channel.guild.id != self.guild_id:
            print("Channel is not in the specified guild.")
            return

        try:
            # Collect the audit log entries into a list
            audit_logs = [entry async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_create, limit=1)]
            
            if audit_logs:
                print(f"Channel created by: {audit_logs[0].user.name}")
                if audit_logs[0].user.id == self.ticket_bot:
                    try:
                        embed = discord.Embed(
                            title="Ad Creation Support",
                            description="Welcome to our Ad Creation Ticket Channel!\n\n"
                                        "To create an ad, please provide the following details:\n"
                                        "• Ad Description\n"
                                        "• Server URL\n"
                                        "• Ad Type (e.g., @here, @everyone, Channel)\n"
                                        "• Server Name\n"
                                        "• Ad Image URL (optional)\n"
                                        "Our support team will help you craft the perfect advertisement."
                                        "**NOTE: If the button is not working please use the `**-ad_button**` command ",
                            color=discord.Color.blue()
                        )
                        embed.set_footer(text="Please be as detailed as possible to help us assist you quickly.")

                        # Create Info Button
                        info_button = discord.ui.Button(
                            label="Ad Information",
                            style=discord.ButtonStyle.primary,
                            custom_id="ad_info"
                        )

                        async def info_button_callback(interaction: discord.Interaction):
                            embed_info = discord.Embed(
                                title="How to Create Ads",
                                description="This system allows you to create advertisements and share them on various platforms. "
                                            "To create an ad, simply click the 'Create Ad' button and provide the necessary details. ",
                                color=discord.Color.blue()
                            )
                            embed_info.add_field(name="What is an Ad?", value="An ad is a promotional message that you can share on various platforms to promote your server or product.")
                            embed_info.add_field(name="How to Create an Ad?", value="To create an ad, click the 'Create Ad' button and follow the instructions provided.")
                            embed_info.add_field(name="What Information is Needed?", value="To create an ad, you need to provide the following information:• Ad Description (What is your ad about?)\n• Server URL (For join the server)\n• Ad Type (@everyone, @here, or Channel)\n• Server Name (What is the name of your server?)\n• Ad Image URL (Optional URL of an image for your ad)", inline=False)
                            embed_info.add_field(
                                name="What Happens After Creating an Ad?",
                                value="Once your ad is created, the bot will generate an embed containing your ad details and send it to the <#1322325865518071910> channel.\n"
                                    "If you select 'Channel' as the Ad Type, the bot will create a new channel named after your server and send the ad there, "
                                    "also mentioning @everyone to ensure it reaches the entire community.\n"
                                    "If you select '@everyone' or '@here' as the Ad Type, the bot will mention everyone in the server, ensuring maximum visibility for your ad. ", inline=False)


                            embed_info.set_footer(text="Please reach out to our support if you have any questions.")
                            await interaction.response.send_message(content="Hey listen Im not typing all of that to ignore it and then you go to open ticket and say : how i can creat ad or waht is and ad or i want more information about ads OKAY!?",embed=embed_info, ephemeral=True)

                        info_button.callback = info_button_callback
                        
                        # Send the button to create ad
                        view = AdView(self.bot)
                        view.add_item(info_button)
                        await asyncio.sleep(2)
                        sellers_role = channel.guild.get_role(int(os.getenv("SELLER_ROLE_ID")))
                        message = await channel.send(content=sellers_role.mention, embed=embed, view=view)

                        await channel.send(f"> HI there!\nPls after any of our seller start talking with you please use /signin commands to save your order in our Database and then you can start talking with our seller.\n\nAfter that user `**-need <wahtever>**`, that will help our seller to know waht you need from him ")
                        


                        # Insert new ticket into the database with placeholders for `claimed_by`, `client_id`, and `client_need`
                        cursor = self.db_connection.cursor()
                        cursor.execute("""
                            INSERT INTO tickets (
                                user_id, 
                                channel_id, 
                                ticket_id, 
                                channel_name, 
                                ticket_name, 
                                claimed_by, 
                                client_id, 
                                client_need
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            None,              # None (who created the ticket)
                            channel.id,        # channel_id
                            channel.id,        # ticket_id (using channel id)
                            channel.name,      # channel_name
                            channel.name,      # ticket_name (using channel name)
                            None,              # claimed_by (default NULL)
                            None,              # client_id (this is the user who triggered the interaction)
                            None               # client_need (default NULL)
                        ))
                        self.db_connection.commit()
                        cursor.close()
                        print(f"Ticket for channel {channel.name} inserted into database.")

                    except Exception as e:
                        print(f"Failed to send message in ticket channel: {e}")
            else:
                print("No audit log found for the channel creation.")
        except Exception as e:
            print(f"Error fetching audit logs: {e}")

async def setup(bot):
    await bot.add_cog(TicketEvent(bot))
