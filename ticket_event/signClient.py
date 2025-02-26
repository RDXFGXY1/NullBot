import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import mysql.connector

load_dotenv()  # Load environment variables

class SignClient(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_connection = self.get_db_connection()

    def get_db_connection(self):
        """Establish a connection to the MySQL database."""
        return mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )

    @discord.app_commands.command(name="signin", description="Sign in to the current ticket channel.")
    async def signin(self, interaction: discord.Interaction):
        """Handle the sign-in slash command."""
        cursor = self.db_connection.cursor(dictionary=True)
        try:
            # Fetch all ticket channel IDs from the database
            cursor.execute("SELECT channel_id FROM tickets")
            ticket_channels = [int(row['channel_id']) for row in cursor.fetchall()]

            if interaction.channel.id not in ticket_channels:
                # Message is not in a ticket channel from the database
                await interaction.response.send_message(
                    f"This channel is not a recognized ticket channel.", ephemeral=True)
                return

            # Check if the user has already signed in this channel
            cursor.execute(
                "SELECT user_id FROM tickets WHERE channel_id = %s",
                (interaction.channel.id,)
            )
            ticket = cursor.fetchone()

            if ticket and ticket['user_id'] == interaction.user.id:
                # User has already signed in
                await interaction.response.send_message(
                    f"You have already signed in.", ephemeral=True)
                return

            # Update the user_id and client_id in the database
            cursor.execute(
                "UPDATE tickets SET user_id = %s, client_id = %s WHERE channel_id = %s",
                (interaction.user.id, interaction.user.id, interaction.channel.id)
            )
            self.db_connection.commit()
            await interaction.response.send_message(
                f"{interaction.user.mention}, you have been signed in successfully.")

        except mysql.connector.Error as err:
            await interaction.response.send_message(
                f"An error occurred: {err}", ephemeral=True)
        finally:
            cursor.close()

async def setup(bot):
    await bot.add_cog(SignClient(bot))
