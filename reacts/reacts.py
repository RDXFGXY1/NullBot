import discord
from discord.ext import commands
import asyncio

class DropSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def drop(self, ctx, emoji: str, reactions_needed: int, *, reward: str):
        """
        Start a drop event. The reward will drop once the reaction count is met.
        
        Usage: !drop <emoji> <reactions_needed> <reward>
        Example: !drop 🎉 5 Free Nitro!
        """
        # Validate the emoji and reactions_needed
        if reactions_needed < 1:
            await ctx.send("❌ The reactions needed must be at least 1.")
            return
        if reactions_needed > 1000:
            await ctx.send("❌ The reactions needed must be no more than 1000.")
            return

        embed = discord.Embed(
            title="🎉 A Drop Has Started!",
            description=(
                f"React with {emoji} to claim the reward!\n\n"
                f"**Reward:** {reward}\n"
                f"**Reactions Needed:** {reactions_needed}"
            ),
            color=discord.Color.gold()
        )
        
        # Send the message and add the reaction emoji
        message = await ctx.send(embed=embed)
        await message.add_reaction(emoji)

        # Log channel or setup a log for drop events
        log_channel = discord.utils.get(ctx.guild.text_channels, name="drop-logs")
        if log_channel:
            log_embed = discord.Embed(
                title="Drop Event Started",
                description=f"Drop event initiated in {ctx.channel.mention} by {ctx.author.mention}.",
                color=discord.Color.blue()
            )
            log_embed.add_field(name="Reward", value=reward)
            log_embed.add_field(name="Reactions Needed", value=reactions_needed)
            log_embed.add_field(name="Emoji", value=emoji)
            await log_channel.send(embed=log_embed)

        def check(reaction, user):
            return (
                reaction.message.id == message.id
                and str(reaction.emoji) == emoji
                and reaction.count >= reactions_needed + 1  # +1 for the bot's reaction
                and not user.bot  # Ignore bot reactions
            )

        try:
            # Set a time limit for the drop (e.g., 30 minutes)
            timeout = 30 * 60  # 30 minutes in seconds
            await self.bot.wait_for("reaction_add", check=check, timeout=timeout)

            # Announce that the reward has been dropped
            await ctx.send(f"🎉 **The reward has dropped!**\n**Reward:** {reward}")
            
            # Optional: log the success in the drop log channel
            if log_channel:
                log_embed = discord.Embed(
                    title="Drop Event Completed",
                    description=f"The drop event in {ctx.channel.mention} has been successfully completed.",
                    color=discord.Color.green()
                )
                log_embed.add_field(name="Winner", value="Someone who reacted!")
                log_embed.add_field(name="Reward", value=reward)
                await log_channel.send(embed=log_embed)
        
        except asyncio.TimeoutError:
            await ctx.send(f"⚠️ **The drop event timed out.** No one reacted in time for the reward: {reward}")
            
            # Optional: log the timeout in the drop log channel
            if log_channel:
                log_embed = discord.Embed(
                    title="Drop Event Timed Out",
                    description=f"The drop event in {ctx.channel.mention} timed out due to lack of reactions.",
                    color=discord.Color.red()
                )
                log_embed.add_field(name="Reward", value=reward)
                log_embed.add_field(name="Reactions Needed", value=reactions_needed)
                await log_channel.send(embed=log_embed)

        except Exception as e:
            await ctx.send(f"⚠️ An error occurred: {e}")
            # Log any errors
            if log_channel:
                log_embed = discord.Embed(
                    title="Drop Event Error",
                    description=f"An error occurred in the drop event in {ctx.channel.mention}.",
                    color=discord.Color.red()
                )
                log_embed.add_field(name="Error", value=str(e))
                await log_channel.send(embed=log_embed)

# Add the cog to the bot
async def setup(bot):
    await bot.add_cog(DropSystem(bot))
