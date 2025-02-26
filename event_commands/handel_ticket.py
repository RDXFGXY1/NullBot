import discord
from discord.ext import commands, tasks
import mysql.connector
import os

class HandleTicket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_connection = self.get_db_connection()
        self.cleanup_task.start()  # Start the cleanup task

    def get_db_connection(self):
        """Establish a connection to the MySQL database."""
        return mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
    
    @tasks.loop(seconds=10)  # This makes the task run every 10 seconds
    async def cleanup_task(self):
        """Compare ticket channels in the database with the guild and clean up missing ones."""
        guild = self.bot.get_guild(int(os.getenv("GUILD_ID")))  # Replace with your guild ID or get it dynamically
        if guild is None:
            print("Guild not found!")
            return

        cursor = self.db_connection.cursor(dictionary=True)
        try:
            # Fetch all ticket channel IDs from the database
            cursor.execute("SELECT channel_id FROM tickets")
            ticket_channels_db = [int(row['channel_id']) for row in cursor.fetchall()]

            # Get all channel IDs from the guild
            ticket_channels_guild = [channel.id for channel in guild.channels]

            # Identify channels that are in the database but not in the guild
            channels_to_delete = [channel_id for channel_id in ticket_channels_db if channel_id not in ticket_channels_guild]

            # Delete missing channels from the database
            for channel_id in channels_to_delete:
                cursor.execute("DELETE FROM tickets WHERE channel_id = %s", (channel_id,))
                self.db_connection.commit()
                print(f"Deleted ticket channel {channel_id} from the database.")

            # Output for successful cleanup
            if channels_to_delete:
                print(f"Cleaned up {len(channels_to_delete)} ticket(s) from the database.")
            else:
                print("No orphaned ticket channels found.")
        
        except mysql.connector.Error as err:
            print(f"Database error occurred: {err}")
        finally:
            cursor.close()

    @cleanup_task.before_loop
    async def before_cleanup(self):
        """Make sure the task waits until the bot is ready."""
        print("Waiting for bot to be ready...")
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(HandleTicket(bot))
