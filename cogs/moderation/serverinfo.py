import discord
import time
from discord import app_commands
from discord.ext import commands
from colorama import Style, Fore
import datetime
from globalvar import footercontent

class Serverinfo(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.tree.on_error = self.on_app_command_error

    @app_commands.command(name="serverinfo", description="Get information about the server.")
    async def serverinfo(self, interaction:discord.Interaction):
        embed = discord.Embed(title="Server Info", 
                          description=f"Here's the server info on `{interaction.guild.name}`", 
                          color= discord.Color.blue(), 
                          timestamp= datetime.datetime.utcnow())
        embed.set_thumbnail(url=interaction.guild.icon)
        embed.set_image(url=interaction.guild.banner)
        embed.add_field(name="Members", value = interaction.guild.member_count)
        embed.add_field(name="Channels", value = f"{len(interaction.guild.text_channels)} Text | {len(interaction.guild.voice_channels)} Voice")
        embed.add_field(name="Created At", value = interaction.guild.created_at.strftime("%b %d, %Y, %T"))
        embed.add_field(name="Owner", value = interaction.guild.owner.mention)
        embed.add_field(name="Roles", value = len(interaction.guild.roles))
        embed.add_field(name="Boost Level", value = interaction.guild.premium_tier)
        embed.add_field(name="Description", value = interaction.guild.description, inline=False)
        embed.set_footer(text=footercontent["text"], icon_url=footercontent["icon_url"])
        await interaction.response.send_message(embed=embed)
    
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
    await bot.add_cog(Serverinfo(bot))