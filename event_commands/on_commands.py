import discord
from discord.ext import commands
from datetime import datetime
from colorama import (
    init,
    Fore,
    Style,
    Back,
)

init = init(autoreset=True)


class LoggingToTerminal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context):
        """Triggered when a command is used."""
        #? Log details to the terminal
        full_command = f"{ctx.prefix}{ctx.command} {' '.join(map(str, ctx.args[1:]))}"
        log_message = (
            f"[{Fore.YELLOW}{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}]"
            f" {Fore.GREEN}COMMAND USED:{Style.RESET_ALL} {ctx.command} | FULL COMMAND: {full_command} |"
            f" {Fore.CYAN}USER:{Style.RESET_ALL} {ctx.author} ({ctx.author.id}) |"
            f" {Fore.MAGENTA}CHANNEL:{Style.RESET_ALL} {ctx.channel} ({ctx.channel.id}) |"
            f" {Fore.BLUE}GUILD:{Style.RESET_ALL} {ctx.guild.name} ({ctx.guild.id})"
            f"{Style.RESET_ALL}"
        )
        print(log_message)

# Add this cog to your bot
async def setup(bot):
    await bot.add_cog(LoggingToTerminal(bot))
