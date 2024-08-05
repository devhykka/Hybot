import discord
import time
from discord import app_commands
from discord.ext import commands
from colorama import Style, Fore

class Ping(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.tree.on_error = self.on_app_command_error

    @app_commands.command(name="ping", description="Request the bots current latency.")
    async def ping(self, interaction:discord.Interaction):
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(description=f":satellite: Current Latency: {latency}ms", color= discord.Color.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # ERROR HANDLER
    async def on_app_command_error(self, interaction: discord.Interaction, error):
        prfx = (Fore.CYAN + time.strftime("%H:%M:%S UTC", time.gmtime()) + Fore.WHITE + Style.BRIGHT)
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message("This command is on cooldown!", ephemeral=True)
        elif isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("You don't have permission to run this command!", ephemeral=True)
        elif isinstance(error, app_commands.MissingRequiredArgument):
            await interaction.response.send_message("Incorrect usage, please try again!", ephemeral=True)
        else:
            await interaction.response.send_message(f"An unexpected error occured! Error: `{error}`", ephemeral=True)
            print(prfx + " Error Handler " + Fore.MAGENTA + f"{error}")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Ping(bot))