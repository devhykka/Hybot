import discord
from discord import app_commands
from discord.ext import commands
from colorama import Fore, Style
import time

class Unmute(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.tree.on_error = self.on_app_command_error

    @app_commands.command(name="unmute", description="Unmuted a muted member of the server.")
    @app_commands.describe(user = "The user you want to unmute.")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def unmute(self, interaction: discord.Interaction, user: discord.Member):
        try:
            if not user.is_timed_out():
                return await interaction.response.send_message(f"{user.mention} is already unmuted!", ephemeral=True)
            await user.timeout(None)
            await interaction.response.send_message(f":speaker: {user.mention} has been unmuted.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("don't have the permissions to unmute this member.", ephemeral=True)
        except discord.HTTPException as error:
            await interaction.response.send_message(f"An unexpected error occured! Error: `{error}`", ephemeral=True)

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
    await bot.add_cog(Unmute(bot))