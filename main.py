import discord
from discord.ext import commands, tasks
from discord import app_commands
from discord import ButtonStyle, Interaction, Member, Embed, Attachment
from discord.ui import Button, View
import asyncio
import os
from dotenv import load_dotenv
import json
from tabulate import tabulate
from colorama import init, Fore, Style, Back
from cogs.event_commands.handel_ticket import HandleTicket


# Initialize colorama
init(autoreset=True)

# Load environment variables

load_dotenv()
TOKEN = os.getenv('TOKEN')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True
intents.presences = True

# disabel help commands
client = commands.Bot(command_prefix=f"{os.getenv("BOT_PREFIX")}", intents=discord.Intents.all())

admin_channel_id = 1312097422851309608
thread_channel_id = 1312097286431571968
admin_role_ids = [1311653738074865685, 1311653723000279090]
db_config = {
    'host': 'mysql.db.bot-hosting.net',
    'user': 'u161499_bryBurlBJW',
    'password': '^hHClJ0yypSwr^l94DwE=Px.',
    'database': 's161499_Logic'
}

@client.event
async def on_ready():
    print(f'Logged in as {Fore.GREEN} {client.user.name} {Style.RESET_ALL} {Fore.YELLOW} ({client.user.id}) {Style.RESET_ALL}')
    await load_cogs()
    await client.tree.sync()
    print("Commands synced")

    server_info_list = []

    for guild in client.guilds:
        # Fetch basic server info
        server_name = guild.name
        server_id = guild.id
        owner = f"{guild.owner.name}#{guild.owner.discriminator}"
        member_count = guild.member_count
        creation_date = guild.created_at.strftime("%Y-%m-%d")
        total_roles = len(guild.roles)
        channel_count = len(guild.channels)

        # Fetch invite details
        invites = 'No Access'
        try:
            invites_list = await guild.invites()  # Await inside async function
            invites = len(invites_list)
        except discord.Forbidden:
            invites = 'No Access'

        # Fetch banned members
        banned_users = 'No Access'
        try:
            banned_users_list = [ban async for ban in guild.bans()]  # Collect banned users
            banned_users = len(banned_users_list)
        except discord.Forbidden:
            banned_users = 'No Access'

        # Append collected info to the list
        server_info_list.append([
            server_name,
            str(server_id),
            owner,
            str(member_count),
            str(banned_users),
            str(total_roles),
        ])

    # Create table layout with more columns
    table = tabulate(
        server_info_list,
        headers=[
            "Server Name", "Server ID", "Owner", "Members", 
            "Banned Users", "Total Roles", 
        ], 
        tablefmt="fancy_grid"
    )

    print(table)
    # Send table in a specific channel
    admin_channel = client.get_channel(int(os.getenv("UPDATES_CHANNEL")))  # Replace with your channel ID
    await admin_channel.send(f"Bot is Online <a:online:1311800904613363793> \n```js\n{table}\n```")

async def load_cogs():
    for root, dirs, files in os.walk('./cogs'):
        for filename in files:
            if filename.endswith('.py') and filename != "__init__.py":
                # Calculate the relative path
                relative_path = os.path.relpath(os.path.join(root, filename), './cogs')
                # Replace the file separator with dots and remove the .py extension
                module_name = relative_path.replace(os.sep, '.')[:-3]
                try:
                    await client.load_extension(f'cogs.{module_name}')
                    print(f'{Fore.BLUE}[INFO]\t{Fore.GREEN} Loaded extension: {Style.RESET_ALL} {module_name}')
                except Exception as e:
                    print(f'{Fore.BLUE}[INFO]\t{Fore.RED} Failed to load extension {Fore.CYAN} {module_name} {Fore.YELLOW} : {type(e).__name__} {Fore.WHITE} - {Back.RED} {e} {Style.RESET_ALL}')


@client.tree.command(name="report", description="Let us know about an issue or user! 🌟")
@app_commands.describe(issue="What's the issue or who are you reporting?", report_type="What type of report is this?", image="Add an image (optional)")
async def report(
    interaction: Interaction, 
    reported_user: Member,
    issue: str, 
    report_type: str, 
    image: Attachment = None
):
    reporter = interaction.user
    guild = interaction.guild
    
    # Get the channel where the report will be sent (admins' channel)

    admin_channel = client.get_channel(admin_channel_id)

    # Create an embed for the report
    embed = Embed(title="📝 New Report", color=discord.Color.blue())
    embed.add_field(name="📣 Reporter", value=reporter.mention, inline=True)
    embed.add_field(name="🚨 Reported User", value=reported_user.mention, inline=True)
    embed.add_field(name="📋 Report Type", value=report_type, inline=False)
    embed.add_field(name="💬 Issue Description", value=issue, inline=False)
    embed.add_field(name="🌐 Guild", value=guild.name, inline=False)

    # If there's an image, add it to the embed
    if image:
        embed.set_image(url=image.url)

    # Create buttons for thread actions (Create and Close)
    class OpenThreadButton(Button):
        def __init__(self):
            super().__init__(label="Open Thread", style=ButtonStyle.primary )

        async def callback(self, interaction: Interaction):
            # Check if the user has the correct admin role
            if any(role.id in admin_role_ids for role in interaction.user.roles):
                # Get the channel where the thread will be created
                thread_channel = client.get_channel(thread_channel_id)
                if thread_channel:
                    thread = await thread_channel.create_thread(
                        name=f"Report: {reporter.name} vs {reported_user.name}",
                        type=discord.ChannelType.public_thread
                    )
                    view=View()
                    view.add_item(CloseThreadButton())
                    
                    # Mention reporter and reported user in the thread
                    await thread.send(f"Hey <@&1272622537624256627> and <@&1272660355465875558>! 👋 \nA new report has been created by {reporter.mention} about {reported_user.mention}. \nReport Type: {report_type}", view=view)
                    await interaction.response.send_message("✨ Thread created successfully! Check it out.", ephemeral=True)
                else:
                    await interaction.response.send_message("Oops! I couldn’t find the thread channel. 😅", ephemeral=True)
            else:
                await interaction.response.send_message("Sorry, you don’t have permission to open a thread. 🚫", ephemeral=True)

    class CloseThreadButton(Button):
        def __init__(self):
            super().__init__(label="Close Thread", style=ButtonStyle.danger)

        async def callback(self, interaction: Interaction):
            # Check if the user has the correct admin role
            if any(role.id in admin_role_ids for role in interaction.user.roles):
                # Close the thread
                if isinstance(interaction.channel, discord.Thread):
                    await interaction.channel.delete()
                    await interaction.response.send_message("🛑 Thread closed successfully.", ephemeral=True)
                else:
                    await interaction.response.send_message("This is not a thread. Can’t close it! 😅", ephemeral=True)
            else:
                await interaction.response.send_message("Sorry, you don’t have permission to close this thread. 🚫", ephemeral=True)

    # Add the buttons to the view (for admins)
    view = View()
    view.add_item(OpenThreadButton())

    # Send the embed with the buttons to the admins' channel
    if admin_channel:
        await admin_channel.send("Hey admins! Use the buttons below to manage this report. 😊", embed=embed, view=view)

    # Send a confirmation message to the user
    await interaction.response.send_message(
        f"Thank you so much, {reporter.mention}! 🎉 Your report has been sent to the admins and they'll handle it soon.",
        ephemeral=True  # Only visible to the user who issued the command
    )

# Fix for autocomplete function
@report.autocomplete('report_type')
async def report_type_autocomplete(interaction: discord.Interaction, current: str):
    options = [
        "User Spam",
        "Bot Error",
        "User Report",
        "User Link",
        "Other"
    ]
    filtered_options = [option for option in options if current.lower() in option.lower()]
    return [app_commands.Choice(name=option, value=option) for option in filtered_options]

client.run(TOKEN)