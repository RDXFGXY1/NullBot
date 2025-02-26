import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

class WebhookManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="sendwebhook", aliases=["sb"])
    @commands.has_any_role(int(os.getenv("DEVLOPER_ROLE_ID")))
    async def send_webhook(self, ctx, *args):
        """
        Send a webhook with dynamic options:
        - `-normal`: Send using the bot's name and avatar.
        - `-user <user_id>`: Send using the user's nickname and avatar.
        - `-image <link>`: Add an image to the message.
        - `-name <text>`: Set a custom webhook name.
        - `-Uprofile <link>`: Set a custom webhook profile picture.
        Example: 
        `BOT_PREFIX=-v send_webhook -user 123456789 "Hello from user!" -image <image_link> -name AnnounceBot -Uprofile <avatar_link>`
        """
        args = list(args)
        message_content = None
        webhook_name = None
        webhook_avatar = None
        embed_image = None

        # Parse flags and arguments
        if "-normal" in args:
            args.remove("-normal")
            webhook_name = self.bot.user.name
            webhook_avatar = self.bot.user.avatar.url

        if "-user" in args:
            user_index = args.index("-user")
            try:
                user_id = int(args[user_index + 1])
                user = ctx.guild.get_member(user_id)
                if not user:
                    await ctx.send("User not found in the server!")
                    return
                args.pop(user_index + 1)
                args.remove("-user")
                webhook_name = user.nick if user.nick else user.name
                webhook_avatar = user.avatar.url if user.avatar else None
            except (ValueError, IndexError):
                await ctx.send("Invalid `-user` argument. Use `-user <user_id>`.")
                return

        if "-name" in args:
            name_index = args.index("-name")
            try:
                webhook_name = args.pop(name_index + 1)
                args.remove("-name")
            except IndexError:
                await ctx.send("You must provide a name after `-name`.")
                return

        if "-Uprofile" in args:
            avatar_index = args.index("-Uprofile")
            try:
                webhook_avatar = args.pop(avatar_index + 1)
                args.remove("-Uprofile")
            except IndexError:
                await ctx.send("You must provide a link after `-Uprofile`.")
                return

        if "-image" in args:
            image_index = args.index("-image")
            try:
                embed_image = args.pop(image_index + 1)
                args.remove("-image")
            except IndexError:
                await ctx.send("You must provide a link after `-image`.")
                return

        # Remaining args are the message content
        message_content = " ".join(args)
        if not message_content:
            await ctx.send("You must provide a message to send!")
            return

        # Create a temporary webhook in the current channel
        try:
            webhook = await ctx.channel.create_webhook(name=webhook_name or "TempWebhook")
            embed = None

            if embed_image:
                embed = discord.Embed(description=message_content, color=discord.Color.blue())
                embed.set_image(url=embed_image)

            await webhook.send(
                content=message_content if not embed else None,
                username=webhook_name or "TempWebhook",
                avatar_url=webhook_avatar or None,
                embed=embed,
            )
            await webhook.delete()  # Delete the webhook after use
            await ctx.message.delete()  # Optionally delete the command message
        except discord.Forbidden:
            await ctx.send("I don't have permission to manage webhooks in this channel.")
        except discord.HTTPException as e:
            await ctx.send(f"Failed to send webhook: {e}")



    @send_webhook.error
    async def send_webhook_error(self, ctx, error):
        if isinstance(error, commands.MissingAnyRole):
            await ctx.send(
                "**You don't have permission to use this command.**\n"
                "# <a:error:1311805750695428158> : If someone reports you for using this command illegally, you will be banned from the server."
            )
        else:
            await ctx.send(f"An unexpected error occurred: {error}")


# Add the cog to the bot
async def setup(bot):
    await bot.add_cog(WebhookManager(bot))
