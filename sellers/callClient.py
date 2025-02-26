import discord
from discord.ext import commands
from discord.ui import View, Button
import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """Establish a connection to the database using environment variables."""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

class CallClient(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_role(int(os.getenv("SELLER_ROLE_ID")))
    @commands.command(name="call", aliases=["aji", "callclient"], description="Call a client associated with the current ticket.")
    async def call_client(self, ctx):
        """Calls a client associated with the current ticket and sends a DM."""
        connection = None
        cursor = None

        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)

            # Query to fetch the client ID associated with the current channel (ticket)
            cursor.execute("SELECT client_id FROM tickets WHERE channel_id = %s", (ctx.channel.id,))
            result = cursor.fetchone()

            if result and result['client_id']:
                client_id = result['client_id']
                user = await self.bot.fetch_user(client_id)
                
                embed = discord.Embed(
                    title="You Are Being Called!",
                    description=f"A seller is calling you regarding your ticket in {ctx.guild.name}. Please respond at your earliest convenience.",
                    color=discord.Color.blue()
                )
                embed.set_footer(text="Thank you for your prompt attention.")
                embed.set_thumbnail(url=ctx.guild.icon.url)
                #? button wiht channel link
                view = View()
                view.add_item(Button(label="Join Channel", url=ctx.channel.jump_url))
                
                if user:
                    await user.send(embed=embed, view=view)
                    await ctx.send("✅ The client has been notified via DM.")
                else:
                    await ctx.send("❌ Unable to send DM to the client. Please check their availability.")
            else:
                await ctx.send("❌ No client ID found for this ticket. Please ensure this is a valid ticket channel.")
        
        except mysql.connector.Error as err:
            await ctx.send(f"🚨 Database error: {err}")
        
        except discord.Forbidden:
            await ctx.send("❌ Unable to send DM to the client. They may have DMs disabled.")
        
        except Exception as e:
            await ctx.send(f"🚨 An unexpected error occurred: {e}")
        
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    @call_client.error
    async def call_client_error(self, ctx, error):
        """Handles errors for the call_client command."""
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You lack the necessary permissions to use this command.")
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send("🚨 There was an error processing the command. Please try again later.")
        else:
            await ctx.send("❌ An unknown error occurred.")

async def setup(bot):
    """Setup function to add the CallClient cog to the bot."""
    await bot.add_cog(CallClient(bot))
