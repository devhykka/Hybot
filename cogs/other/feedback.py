import discord
import time
from discord import app_commands, ui
from discord.ext import commands
from colorama import Fore, Style

class Feedback(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="feedback", description="Give feedback to the developers of the bot!")
    async def Feedback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(FeedbackModal(self.bot))  # Pass bot instance to FeedbackModal
    
    # ERROR HANDLER
    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        prfx = (Fore.CYAN + time.strftime("%H:%M:%S UTC", time.gmtime()) + Fore.WHITE + Style.BRIGHT)
        await interaction.response.send_message(f"An unexpected error occured! Error: `{error}`", ephemeral=True)
        print(prfx + " Error Handler " + Fore.MAGENTA + f"{error}")

class FeedbackModal(ui.Modal, title="Developer Feedback"):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        
    username = ui.TextInput(label="Enter your username", 
                            style=discord.TextStyle.short, 
                            required=True)
    feedback = ui.TextInput(label="Feedback", 
                            placeholder="Type your feedback here...\n"
                                        "Suggest a new feature or report a bug!",
                            style=discord.TextStyle.long, 
                            required=True,
                            max_length=300)

    async def on_submit(self, interaction: discord.Interaction):
        feedback_guild_id = 1250100620472619018
        feedback_channel_id = 1255196650876702730
        feedback_guild = self.bot.get_guild(feedback_guild_id)
        
        if feedback_guild is None:
            await interaction.response.send_message("Feedback guild not found. Please contact the bot owner.", ephemeral=True)
            return
        
        feedback_channel = feedback_guild.get_channel(feedback_channel_id)
        
        if feedback_channel is None:
            await interaction.response.send_message("Feedback channel not found. Please contact the bot owner.", ephemeral=True)
            return

        sender_guild_invite = await interaction.channel.create_invite(max_age=0, max_uses=0)

        embed = discord.Embed(title=":books: Feedback", 
                              description=f"Username: {interaction.user.name} ({interaction.user.id})\n"
                                          f"Sent from: [{interaction.guild.name}]({sender_guild_invite.url}) ({interaction.guild.id})", 
                              color=0x2f3136)
        embed.add_field(name="Contents:", value=f"{self.feedback.value}", inline=False)

        try:
            await feedback_channel.send(embed=embed)
            await interaction.response.send_message(f'Thank you for your feedback.', ephemeral=True)
        except Exception as error:
            prfx = (Fore.CYAN + time.strftime("%H:%M:%S UTC", time.gmtime()) + Fore.WHITE + Style.BRIGHT)
            await interaction.response.send_message(f"An unexpected error occurred! Error: `{error}`", ephemeral=True)
            print(prfx + " Error Handler " + Fore.MAGENTA + f"{error}")
    
    # ERROR HANDLER
    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        prfx = (Fore.CYAN + time.strftime("%H:%M:%S UTC", time.gmtime()) + Fore.WHITE + Style.BRIGHT)
        await interaction.response.send_message(f"An unexpected error occured! Error: `{error}`", ephemeral=True)
        print(prfx + " Error Handler " + Fore.MAGENTA + f"{error}")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Feedback(bot))