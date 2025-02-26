import discord
from discord.ext import commands
import json
from dotenv import load_dotenv
import os

load_dotenv()

class WarnSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warns_file = os.getenv("WARN_FILE")
        self.load_warns()

    def load_warns(self):
        """Load warnings from a file."""
        try:
            with open(self.warns_file, "r") as f:
                self.warns = json.load(f)
        except FileNotFoundError:
            self.warns = {}

    def save_warns(self):
        """Save warnings to a file."""
        with open(self.warns_file, "w") as f:
            json.dump(self.warns, f, indent=4)

    @commands.command(name="warn")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        os.makedirs("server/warns", exist_ok=True)
        
        """Warn a user."""
        if str(member.id) not in self.warns:
            self.warns[str(member.id)] = []

        # Add the warning
        self.warns[str(member.id)].append({"reason": reason, "moderator": str(ctx.author), "time": str(ctx.message.created_at)})
        self.save_warns()

        # Notify in chat
        await ctx.send(f"✅ {member.mention} has been warned for: **{reason}**")
        try:
            await member.send(f"You have been warned in {ctx.guild.name} for: **{reason}**")
        except discord.Forbidden:
            pass

    @commands.command(name="warnings")
    @commands.has_permissions(manage_messages=True)
    async def warnings(self, ctx, member: discord.Member):
        """View warnings for a user."""
        user_warns = self.warns.get(str(member.id), [])

        if not user_warns:
            await ctx.send(f"ℹ️ {member.mention} has no warnings.")
        else:
            embed = discord.Embed(title=f"Warnings for {member.name}", color=discord.Color.orange())
            for i, warn in enumerate(user_warns, start=1):
                embed.add_field(
                    name=f"Warning #{i}",
                    value=f"**Reason:** {warn['reason']}\n**Moderator:** {warn['moderator']}\n**Time:** {warn['time']}",
                    inline=False
                )
            await ctx.send(embed=embed)

    @commands.command(name="clearwarns")
    @commands.has_permissions(manage_messages=True)
    async def clear_warnings(self, ctx, member: discord.Member):
        """Clear all warnings for a user."""
        if str(member.id) in self.warns:
            self.warns.pop(str(member.id))
            self.save_warns()
            await ctx.send(f"✅ Cleared all warnings for {member.mention}.")
        else:
            await ctx.send(f"ℹ️ {member.mention} has no warnings to clear.")

        
    @warnings.error
    async def warnings_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specify a member to view warnings for.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("Could not find that member.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have permission to view warnings.")


# Add this cog to your bot
async def setup(bot):
    await bot.add_cog(WarnSystem(bot))
