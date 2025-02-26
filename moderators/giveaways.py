import discord
from discord.ext import commands
import mysql.connector
import os
from dotenv import load_dotenv as Load
import asyncio
from datetime import datetime, timedelta
import random

Load()

class Giveaways(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_connection = self.get_db_connection()
        
    def get_db_connection(self):
        return mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )

    @discord.app_commands.command(name="giveaway", description="Create a giveaway")
    async def giveaway(self, interaction: discord.Interaction, duration: str, prize: str, winners: int, image: discord.Attachment = None):
        cursor = self.db_connection.cursor(dictionary=True)
        try:
            # Check if user is signed in
            cursor.execute("SELECT * FROM users WHERE user_id = %s", (interaction.user.id,))
            user = cursor.fetchone()
            if not user:
                await interaction.response.send_message("You must be signed in to create a giveaway.", ephemeral=True)
                return

            # Parse duration into seconds
            try:
                # Remove any spaces and check if the input is valid
                duration = duration.replace(" ", "")  # Remove all spaces
                if len(duration) < 2:
                    await interaction.response.send_message("Invalid duration format. Use `<number> <h|m>` (e.g., `1 h` or `30 m`).", ephemeral=True)
                    return
                
                # Split based on whether it contains 'h' or 'm'
                if "h" in duration:
                    amount = int(duration.replace("h", ""))
                    unit = "h"
                    duration_seconds = amount * 60 * 60  # Convert hours to seconds
                elif "m" in duration:
                    amount = int(duration.replace("m", ""))
                    unit = "m"
                    duration_seconds = amount * 60  # Convert minutes to seconds
                else:
                    await interaction.response.send_message("Invalid duration format. Use `h` for hours or `m` for minutes.", ephemeral=True)
                    return
            except ValueError:
                await interaction.response.send_message("Invalid duration format. Use `<number> <h|m>` (e.g., `1 h` or `30 m`).", ephemeral=True)
                return



            # Create embed for giveaway
            embed = discord.Embed(
                title="🎉 **Giveaway Time!** 🎉",
                description=(
                    f"**Prize:** {prize}\n"
                    f"**Winners:** {winners}\n"
                    f"**Duration:** {duration}\n"
                    f"**Hosted By:** {interaction.user.mention}"
                ),
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()  # Adds a timestamp to the embed
            )

            embed.set_thumbnail(url=interaction.user.avatar.url)  # Set the host's avatar as thumbnail
            embed.add_field(name="📅 Started At", value=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), inline=False)
            embed.set_footer(text="React with 🎉 to enter!", icon_url=interaction.guild.icon.url if interaction.guild.icon else "")

            if image:
                embed.set_image(url=image.url)
            embed.set_footer(text="Ends")

            # Send giveaway message
            await interaction.response.send_message(embed=embed)
            message = await interaction.original_response()
            await message.add_reaction("🎉")
            
            # Wait for the giveaway to end after the specified duration
            await asyncio.sleep(duration_seconds)
            message = await interaction.channel.fetch_message(message.id)

            # Check if there are reactions
            if message.reactions:
                reaction = message.reactions[0]
                # Ensure the reaction has users (excluding the bot)
                users = [user async for user in message.reactions[0].users()]
                users.remove(self.bot.user)  # Remove the bot's reaction from the list
                
                if len(users) < winners:
                    winners = len(users)  # Set winners to available users if there aren't enough

                # Choose random winners
                chosen_winners = "\n".join([f"<@{user.id}>" for user in random.sample(users, winners)])
                end_embed = discord.Embed(
                    title="🎉 **Giveaway Ended!** 🎉",
                    description=(
                        f"**Prize:** {prize}\n"
                        f"**Winners:**\n{chosen_winners}\n\n"
                        f"**Hosted By:** {interaction.user.mention}"
                    ),
                    color=discord.Color.green(),
                    timestamp=datetime.utcnow()  # Adds a timestamp to the embed
                )

                end_embed.set_thumbnail(url=interaction.user.avatar.url)  # Host's avatar as thumbnail
                end_embed.add_field(name="🏆 **Congratulations to the Winners!**", value="Thank you for participating!", inline=False)
                end_embed.add_field(name="📅 Ended At", value=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), inline=False)
                end_embed.set_footer(text="Stay tuned for more giveaways!", icon_url=interaction.guild.icon.url if interaction.guild.icon else "")

                await interaction.followup.send(content=chosen_winners, embed=end_embed)
            else:
                await interaction.followup.send("No reactions were made during the giveaway. No winners could be chosen.")
        except Exception as e:
            print(f"Error: {e}")
            await interaction.followup.send(f"An error occurred: {e}")
        finally:
            cursor.close()

async def setup(bot):
    await bot.add_cog(Giveaways(bot))
