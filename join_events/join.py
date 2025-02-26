import discord
import os
from discord.ext import commands
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class ApplyToTeam(discord.ui.View):
    def __init__(self):
        super().__init__()
        # Button for Apply
        self.add_item(discord.ui.Button(
            label="Apply To Team", 
            style=discord.ButtonStyle.link, 
            url="https://discord.com/channels/824737725961732167/1316526079887802379"
        ))
        # Button for Ticket Order
        self.add_item(discord.ui.Button(
            label="Ticket Order", 
            style=discord.ButtonStyle.link, 
            url="https://discord.com/channels/824737725961732167/1316526079887802379"
        ))


class JoinEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.welcome_channel_id = 1312098797601689640
        self.member_role_id = int(os.getenv("USER_ROLE_ID"))
        self.bot_role_id = int(os.getenv("BOT_ROLE_ID"))

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Assign roles
        try:
            if not member.bot:
                member_role = discord.utils.get(member.guild.roles, id=self.member_role_id)
                if member_role:
                    await member.add_roles(member_role)
            else:
                bot_role = discord.utils.get(member.guild.roles, id=self.bot_role_id)
                if bot_role:
                    await member.add_roles(bot_role)
        except discord.HTTPException as e:
            print(f"⚠️ Failed to assign role: {e}")

        # Get the welcome channel
        welcome_channel = discord.utils.get(member.guild.channels, id=self.welcome_channel_id)
        if welcome_channel and not member.bot:
            # Create a welcome embed
            welcome_embed = discord.Embed(
                title=f"{member.name}",
                description=f"> **Hello : __{member.name}__ .",
                color=discord.Color.blue()
            )
            welcome_embed.add_field(name=f'> Welcome to __{member.guild.name}__', value="We're glad to have you here!")
            welcome_embed.add_field(name=f"> If You Wanna Order Something", value="`%assni nzid tiket room!!` / Or Click The Button Below!")
            welcome_embed.add_field(name=f"> If You Want Join Nova S Team Open Ticket Here", value="[Apply To Team](https://discord.com/channels/824737725961732167/1316526079887802379)")
            welcome_embed.add_field(name=f"> Account Created At", value=f"{member.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            welcome_embed.add_field(name="> Enjoy <3", value="Have a great time!")
            welcome_embed.set_author(name=member.name, icon_url=member.display_avatar.url)
            welcome_embed.set_thumbnail(url=member.display_avatar.url)

            # Send the embed with buttons
            view = ApplyToTeam()
            await welcome_channel.send(embed=welcome_embed, view=view)




async def setup(bot):
    await bot.add_cog(JoinEvents(bot))
