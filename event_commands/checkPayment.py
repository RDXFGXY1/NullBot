import asyncio
from datetime import datetime, timedelta
import mysql.connector
import discord.ext.commands as commands
import discord

class CheckPayments(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_config = {
            'host': 'mysql.db.bot-hosting.net',
            'user': 'u161499_bryBurlBJW',
            'password': '^hHClJ0yypSwr^l94DwE=Px.',
            'database': 's161499_Logic'
        }
        self.bot.loop.create_task(self.payment_check_loop())

    async def payment_check_loop(self):
        while True:
            try:
                await self.check_payments_expiration()
                # Sleep for 1 minute
                await asyncio.sleep(60)
            except Exception as e:
                print(f"Error in payment check loop: {e}")
                await asyncio.sleep(60)  # Wait a minute before retrying

    async def check_payments_expiration(self):
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Query to find payments expiring in 4 days
            cursor.execute("""
                SELECT user_id, expiry_date 
                FROM payments 
                WHERE expiry_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 4 DAY)
            """)
            payments = cursor.fetchall()

            for user_id, expiration_date in payments:
                # Ensure expiration_date is a datetime.date object
                if isinstance(expiration_date, datetime):
                    expiration_date = expiration_date.date()
                
                # Calculate days left
                days_left = (expiration_date - datetime.now().date()).days
                
                # Get Discord user
                member = await self.bot.fetch_user(user_id)
                if member:
                    embed = discord.Embed(
                        title="⚠️ Subscription Expiring Soon",
                        description=f"🕒 Your payment is expiring in **{days_left}** days. Please renew your subscription to continaccessing services.",
                        color=discord.Color.orange()
                    )
                    embed.set_footer(text="Renew Now to Avoid Service Interruption")
                    await member.send(embed=embed)
                    print(f"Sent reminder to {member.name} ({member.id}) for payment expiration.")

            cursor.close()
            conn.close()

        except Exception as e:
            print(f"Error checking payments: {e}")

async def setup(bot):
    await bot.add_cog(CheckPayments(bot))
