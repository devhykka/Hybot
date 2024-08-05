import discord
import datetime
import time
from colorama import Fore, Style
from discord.ext import commands
from discord import app_commands
from globalvar import footercontent

class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.tree.on_error = self.on_app_command_error

    @app_commands.command(name="help", description="Receive a list of commands and information.")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(title="<:hybot:1250122315841273966> HyBot Help",
                      description="Below you can find a list of some useful HyBot commands! Other useful resources: [Support Server](https://discord.gg/2ppk); [Patreon](https://www.patreon.com/hybot); Website.\n\nFor any inquiries about the bot please join the support server and open a ticket.",
                      colour=discord.Color.blue(),
                      timestamp=datetime.datetime.utcnow())
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/1250100620472619021/1250960338556424283/emoji1.png?ex=667aaeda&is=66795d5a&hm=636e1bba02439ff8c047138be4bbf786992d1a53b495d5c4e079d2701627f5f3&=&format=webp&quality=lossless")
        embed.add_field(name="Moderation Commands",
                        value="`/mute` | Timeout a user for a period of time.\n"
                              "`/unmute` | Remove the timeout from a user.\n"
                              "`/kick` | Kick a user from the server.\n"
                              "`/ban`| Ban a user from the server.\n"
                              "`/purge` | Delete messages in bulk.\n"
                              "`/whois` | Get information about a user.\n"
                              "`/serverinfo` | Get information about the server.",
                        inline=False)
        embed.add_field(name="Utility Commands",
                        value="`/help` | Sends this embed.\n"
                              "`/giveaway create` | Host a giveaway.\n"
                              "`/giveaway reroll` | Reroll a giveaway. (Soon:tm:)\n"
                              "`/giveaway delete` | Delete a giveaway. (Soon:tm:)\n"
                              "`/ping` | Get the bot's ping.\n"
                              "`/level` | Get your server level. (Soon:tm:)\n"
                              "`/leaderboard` | See the top 10 users in the server. (Soon:tm:)\n"
                              "`/terms oneplayer` | Get a list of one player parkour terms.\n"
                              "`/terms twoplayer` | Get a list of two player parkour terms.",
                        inline=False)
        embed.add_field(name="Configuration Commands",
                        value="`/config tickets` | Configure the Hybot ticket system.\n"
                              "`/config welcome` | Configure the welcome messages. (Soon:tm:)")
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
    await bot.add_cog(Help(bot))