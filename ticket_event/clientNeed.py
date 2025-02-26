import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import mysql.connector

load_dotenv()

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

class ClientNeed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="need", description="Create a client need ticket")
    async def client_need(self, ctx, *, need_description):
        # Connect to the database
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        try:
            cursor.execute("SELECT channel_id FROM tickets")
            ticket_channels = [channel['channel_id'] for channel in cursor.fetchall()]
            
            if ctx.channel.id not in ticket_channels:
                await ctx.send("❌ This command can only be used in designated ticket channels.")
                return
            
            # Update the client need in the database
            cursor.execute("UPDATE tickets SET client_need = %s WHERE channel_id = %s", (need_description, ctx.channel.id))
            connection.commit()

            # Change the channel name to reflect the client's need
            new_channel_name = f"need-{need_description.replace(' ', '-')[:50]}"  # Limit the length and format the name
            await ctx.channel.edit(name=new_channel_name)
            
            # Notify sellers
            sellers_role_id = os.getenv("SELLER_ROLE_ID")
            sellers_role_mention = f"<@&{sellers_role_id}>"
            await ctx.send(f"{sellers_role_mention} Client __{ctx.author.id}__ Need: {need_description}")
        
        except mysql.connector.Error as err:
            await ctx.send(f"An error occurred: {err}")
        
        finally:
            cursor.close()
            connection.close()

async def setup(bot):
    await bot.add_cog(ClientNeed(bot))
