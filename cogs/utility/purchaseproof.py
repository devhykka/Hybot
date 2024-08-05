import discord
import datetime
import time
from discord.ext import commands
from colorama import Fore, Style
from discord import app_commands

class PurchaseProof(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="purchaseproof", description="Sends the purchase proof embed.")
    async def purchaseproof(self, interaction: discord.Interaction):
        embed = discord.Embed(title="<:eb9:1266120766349512744> Proof of Purchase",
                      description="Please complete any of the following steps to prove your purchase.\n\n"
                                  "**1.)** Provide an in-game screenshot of yourself including the tablist, with your rank clearly visible.\n\n"
                                  "**2.)** Screenshot the receipt of your purchase, sent to you via email.\n\n"
                                  "**3.)** If you can't provide any of this evidence, please wait for a member of staff to manually verify your rank.",
                      colour=0xfd7427,
                      timestamp=datetime.datetime.now())
        
        await interaction.response.send_message("Sent the embed successfully!", ephemeral=True)
        await interaction.followup.send(embed=embed)

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

async def setup(bot):
    await bot.add_cog(PurchaseProof(bot))