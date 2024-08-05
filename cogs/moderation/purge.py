import discord
import time
from discord import app_commands
from discord.ext import commands
from colorama import Style, Fore

class Purge(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.tree.on_error = self.on_app_command_error

    @app_commands.command(name="purge", description="Delete messages in bulk from a channel.")
    @app_commands.describe(count = "Number of messages to purge.")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def purge(self, interaction: discord.Interaction, count: int):
        try:
            if count > 100:
                return await interaction.response.send_message(f"`{count}` is too large. Keep purging under 100 messages.")
            await interaction.response.defer()
            await interaction.channel.purge(limit=count)
            await interaction.followup.send(f":toolbox: Successfully purged {count} messages from the channel.", ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send(":x: I don't have the permissions to do this!", ephemeral=True)
        except discord.HTTPException as error:
            await interaction.followup.send(f":zzz: An unexpected error occured! Error: `{error}`", ephemeral=True)
    
    # ERROR HANDLER
    async def on_app_command_error(self, interaction: discord.Interaction, error):
        prfx = (Fore.CYAN + time.strftime("%H:%M:%S UTC", time.gmtime()) + Fore.WHITE + Style.BRIGHT)
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(":hourglass: This command is on cooldown!", ephemeral=True)
        elif isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(":no_entry: You don't have permission to run this command!", ephemeral=True)
        elif isinstance(error, app_commands.MissingRequiredArgument):
            await interaction.response.send_message(":thinking: Incorrect usage, please try again!", ephemeral=True)
        else:
            await interaction.response.send_message(f":zzz: An unexpected error occured! Error: `{error}`", ephemeral=True)
            print(prfx + " Error Handler " + Fore.MAGENTA + f"{error}")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Purge(bot))