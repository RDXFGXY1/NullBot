import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import mysql.connector

load_dotenv()  # Load environment variables

class claimTicket(commands.Cog):
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

    @commands.has_role(int(os.getenv("SELLER_ROLE_ID")))
    @commands.command(name="claimt")
    
    async def claim_ticket(self, ctx):
        
        """Allows a user to claim a ticket channel."""
        if ctx.channel.type != discord.ChannelType.text:
            await ctx.send("This command can only be used in text channels.")
            return

        channel_id = ctx.channel.id
        user_id = ctx.author.id
        cursor = self.db_connection.cursor(dictionary=True)

        try:
            # Fetch the ticket info
            cursor.execute("SELECT claimed_by FROM tickets WHERE channel_id = %s", (channel_id,))
            ticket = cursor.fetchone()

            if not ticket:
                await ctx.send("This channel is not associated with any ticket.")
                return

            if ticket['claimed_by']:
                if ticket['claimed_by'] == user_id:
                    await ctx.send("You have already claimed this ticket.")
                else:
                    await ctx.message.delete()  # Delete the claim attempt message
                    await ctx.author.send("This ticket has already been claimed by another user.")
                return

            # Update the `claimed_by` field in the database
            cursor.execute(
                "UPDATE tickets SET claimed_by = %s WHERE channel_id = %s",
                (user_id, channel_id)
            )
            self.db_connection.commit()

            # Update the channel topic
            await ctx.channel.edit(topic=f"Claimed by {ctx.author.display_name}")
            await ctx.send(f"Ticket successfully claimed by {ctx.author.mention}.")

        except mysql.connector.Error as err:
            await ctx.send(f"An error occurred: {err}")
        finally:
            cursor.close()

async def setup(bot):
    await bot.add_cog(claimTicket(bot))
