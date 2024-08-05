import discord
import time
import datetime
import json
import mysql.connector
from discord import app_commands
from discord.ext import commands
from typing import Optional
from colorama import Style, Fore
import asyncio

with open('database.json', 'r') as f:
    database = json.load(f)

def get_database_connection():
    return mysql.connector.connect(
        host=database["host"],
        user=database["user"],
        password=database["password"],
        database=database["database"],
        port=database["port"],
        autocommit=True)

async def get_logging_config(guild_id):
    database = get_database_connection()
    cursor = database.cursor(dictionary=True)
    query = "SELECT `logging_channel` FROM `guild_configs` WHERE `guild_id` = %s"
    cursor.execute(query, (guild_id,))
    result = cursor.fetchone()
    database.close()
    return result

async def kicklog(guild: discord.Guild, user: discord.Member, reason):
    config = await get_logging_config(guild.id)
    if not config:
        await guild.response.send_message("Logging configuration not found!", ephemeral=True)
        return

    logging_channel_id = config.get('logging_channel')
    if not logging_channel_id:
        await guild.response.send_message("Logging channel ID not found in the configuration!", ephemeral=True)
        return

    logging_channel = discord.utils.get(guild.text_channels, id=logging_channel_id)
    if logging_channel is None:
        await guild.response.send_message("Unable to find the logging channel!", ephemeral=True)
        return

    embed = discord.Embed(title="Member Kicked",
                          color=discord.Color.orange(),
                          timestamp=datetime.datetime.utcnow())
    embed.set_thumbnail(url=user.avatar.url)
    embed.add_field(name="<:id:1264255119147405401> User Info", value=f"Mention: <@{user.id}>\nID: `{user.id}`", inline=True)
    embed.add_field(name="<:crown:1264255117935251557> Staff Info", value=f"Mention: {guild.me.mention}\nID: `{guild.me.id}`", inline=True)
    embed.add_field(name="<:insights:1264255120732983386> Reason", value=f"{reason}", inline=False)

    try:
        await logging_channel.send(embed=embed)
    except Exception as e:
        await guild.response.send_message(f"Failed to log the kick. Error: `{e}`", ephemeral=True)

class Kick(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.tree.on_error = self.on_app_command_error

    @app_commands.command(name="kick", description="Kick a user from the server.")
    @app_commands.describe(user="The user you wish to kick from the server.")
    @app_commands.describe(reason="Reason for kicking the user from the server.")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, user: discord.Member, *, reason: Optional[str]):
        try:
            await user.kick(reason=reason)
            await interaction.response.send_message(f":boot: **{user.name}** has been kicked for `{reason}`.", ephemeral=True)
            await kicklog(interaction.guild, user, reason)
        except discord.Forbidden:
            await interaction.followup.send("I don't have the permissions to kick this member.", ephemeral=True)
        except discord.HTTPException as error:
            await interaction.followup.send(f"An unexpected error occurred! Error: `{error}`", ephemeral=True)
    
    @commands.Cog.listener()
    async def on_member_remove(self, user):
        await asyncio.sleep(1)
        guild = user.guild
        reason = None
        async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.kick):
            if entry.target.id == user.id:
                reason = entry.reason
                break
        await kicklog(guild, user, reason)


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
            await interaction.response.send_message(f"An unexpected error occurred! Error: `{error}`", ephemeral=True)
            print(prfx + " Error Handler " + Fore.MAGENTA + f"{error}")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Kick(bot))
