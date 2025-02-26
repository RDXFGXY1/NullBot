import discord
from discord.ext import commands
from discord.ui import View, Select, Button
import asyncio
import os

class TicketSystemInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ticket_counter = 1  # Initialize ticket counter
        self.ticket_category_id = int(os.getenv('OPEN_TICKET_CATEGORY'))  # Category for open tickets
        self.closed_category_id = int(os.getenv('CLOSED_TICKET_CATEGORY'))  # Category for closed tickets (you need to set this)

    @commands.command(name="ticketinfo", aliases=["TI"], description="Opens a ticket menu")
    async def ticket(self, ctx):
        await ctx.channel.purge(limit=1)
        view = TicketDropdownView(self)
        embed = discord.Embed(
            title="Ticket System",
            description="Select the type of ticket you wish to open.",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed, view=view)

    @commands.command(name="claim", description="Claim a ticket")
    async def claim_ticket(self, ctx, ticket_id: int):
        """Command to claim a ticket."""
        ticket_channel = discord.utils.get(ctx.guild.text_channels, name=f"ticket-{ticket_id}")
        if not ticket_channel:
            await ctx.send("Ticket not found!")
            return

        # Assuming the staff member claiming the ticket
        staff_member = ctx.author

        # Rename the ticket channel to "claimed-by-{staff_member_name}"
        new_name = f"claimed-by-{staff_member.name}"
        await ticket_channel.edit(name=new_name)

        # Send a message confirming the claim
        await ticket_channel.send(f"Ticket claimed by {staff_member.mention}.")


class TicketDropdownView(View):
    def __init__(self, cog: TicketSystemInfo):
        super().__init__(timeout=None)
        self.add_item(TicketDropdownMenu(cog))

class TicketDropdownMenu(Select):
    def __init__(self, cog: TicketSystemInfo):
        self.cog = cog
        options = [
            discord.SelectOption(label="Technical Support", description="Get help with technical issues", emoji="🛠️"),
            discord.SelectOption(label="Account Issues", description="Report account-related problems", emoji="👤"),
            discord.SelectOption(label="VIP", description="Buy VIP Pass", emoji="💎"),
        ]
        super().__init__(
            placeholder="Choose your ticket type...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        ticket_type = self.values[0]
        guild = interaction.guild
        author = interaction.user

        # Fetch the ticket category
        ticket_category = discord.utils.get(guild.categories, id=self.cog.ticket_category_id)
        if not ticket_category:
            await interaction.response.send_message(
                "Ticket category not found. Please contact an administrator.", ephemeral=True
            )
            return

        # Create a new ticket channel with a sequential ticket number
        ticket_number = self.cog.ticket_counter
        ticket_channel_name = f"ticket-{ticket_number}"

        # Check if the ticket channel already exists
        if discord.utils.get(ticket_category.channels, name=ticket_channel_name):
            await interaction.response.send_message(
                f"A ticket with the name `{ticket_channel_name}` already exists.", ephemeral=True
            )
            return

        # Define roles for permissions
        staff_role = discord.utils.get(guild.roles, name="Staff Team")
        manager_role = discord.utils.get(guild.roles, name="Manager")
        founder_role = discord.utils.get(guild.roles, name="Founder")
        owner_role = discord.utils.get(guild.roles, name="Owner")

        # Default overwrites for the ticket channel
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            author: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        }

        # Adjust permissions based on the ticket type
        if ticket_type == "Technical Support":
            if staff_role:
                overwrites[staff_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)
        elif ticket_type == "Account Issues":
            if manager_role:
                overwrites[manager_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)
            if founder_role:
                overwrites[founder_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)
            if owner_role:
                overwrites[owner_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)
        elif ticket_type == "VIP":
            if owner_role:
                overwrites[owner_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        # Create the ticket channel
        ticket_channel = await ticket_category.create_text_channel(
            name=ticket_channel_name,
            overwrites=overwrites,
            reason=f"Ticket created by {author.name}",
        )

        # Increment the ticket counter for the next ticket
        self.cog.ticket_counter += 1

        # Embed with a fixed image
        embed = discord.Embed(
            title=f"{ticket_type} Ticket",
            description="Please provide detailed information about your issue.",
            color=discord.Color.blue()
        )
        embed.set_footer(text="Use the button below to close this ticket.")

        # Add close button to the ticket channel
        view = TicketCloseButtonView(self.cog, ticket_channel, author)
        await ticket_channel.send(embed=embed, view=view)
        await interaction.response.send_message(
            f"Your {ticket_type} ticket has been created: {ticket_channel.mention}",
            ephemeral=True
        )


class TicketCloseButtonView(View):
    def __init__(self, cog, ticket_channel, author):
        super().__init__(timeout=None)  
        self.add_item(TicketCloseButton(cog, ticket_channel, author))

class TicketCloseButton(Button):
    def __init__(self, cog, ticket_channel, author):
        super().__init__(label="Close Ticket", style=discord.ButtonStyle.danger)
        self.cog = cog
        self.ticket_channel = ticket_channel
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        # Check if the user pressing the button is the ticket creator
        if interaction.user != self.author:
            await interaction.response.send_message(
                "Only the ticket creator can close this ticket.", ephemeral=True
            )
            return

        # Check if the ticket is already in the closed category
        closed_category = discord.utils.get(interaction.guild.categories, id=self.cog.closed_category_id)
        if self.ticket_channel.category == closed_category:
            await interaction.response.send_message(
                "This ticket has already been closed.", ephemeral=True
            )
            return

        await interaction.response.send_message("This ticket will be closed in 5 seconds...")
        await asyncio.sleep(5)

        # Move the ticket to the closed category
        if closed_category:
            await self.ticket_channel.edit(category=closed_category)

        # Rename the channel with the staff member's name
        await self.ticket_channel.edit(name=f"closed-{self.author.name}")

        # Notify the ticket creator
        await self.ticket_channel.send(f"This ticket has been closed by {self.author.mention}.")

        # Optionally log the closure
        logs_category = discord.utils.get(interaction.guild.categories, id=self.cog.logs_category_id)
        if logs_category:
            log_channel = await logs_category.create_text_channel(name=f"log-{self.ticket_channel.name}")
            await log_channel.send(f"Ticket {self.ticket_channel.name} was closed by {self.author.mention}")

async def setup(bot):
    await bot.add_cog(TicketSystemInfo(bot))
