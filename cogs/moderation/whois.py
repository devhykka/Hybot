import discord
import time
from discord import app_commands
from discord.ext import commands
from typing import Optional
from colorama import Style, Fore
import datetime
from globalvar import footercontent

class Whois(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.tree.on_error = self.on_app_command_error

    @app_commands.command(name="whois", description="Get information about another member of the server.")
    async def whois(self, interaction: discord.Interaction, member:discord.Member=None):
        if member == None:
            await interaction.response.send_message("Invalid Usage! Please choose a member to view.", ephemeral=True)
        roles = [roles.mention for roles in member.roles]
        embed = discord.Embed(title="User Info", 
                          description=f"Here's the user info on {member.mention}.", 
                          color= discord.Color.blue(), 
                          timestamp= datetime.datetime.utcnow())
        embed.set_thumbnail(url=member.avatar)
        embed.add_field(name="ID", value = f"`{member.id}`")
        embed.add_field(name="Username", value = f"`{member.name}#{member.discriminator}`")
        embed.add_field(name="Nickname", value = f"`{member.display_name}`")
        embed.add_field(name="Joined Discord", value = member.created_at.strftime("%b %d, %Y, %T"))
        embed.add_field(name="Joined Server", value = member.joined_at.strftime("%b %d, %Y, %T"))
        embed.add_field(name=f"Roles ({len(roles)})", value = ", ".join([roles.mention for roles in member.roles]), inline=False)
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
    await bot.add_cog(Whois(bot))