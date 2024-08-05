import discord
from discord import app_commands, utils
from discord.ext import commands
from typing import Optional
from humanfriendly import parse_timespan, InvalidTimespan
from datetime import timedelta
from colorama import Fore, Style
import time
import json
import datetime
import asyncio
import mysql.connector

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

async def mutelog(guild: discord.Guild, user: discord.Member, reason):
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

    embed = discord.Embed(title="Member Muted",
                          color=discord.Color.yellow(),
                          timestamp=datetime.datetime.utcnow())
    embed.set_thumbnail(url=user.avatar.url)
    embed.add_field(name="<:id:1264255119147405401> User Info", value=f"Mention: <@{user.id}>\nID: `{user.id}`", inline=True)
    embed.add_field(name="<:crown:1264255117935251557> Staff Info", value=f"Mention: {guild.me.mention}\nID: `{guild.me.id}`", inline=True)
    embed.add_field(name="<:insights:1264255120732983386> Reason", value=f"{reason}", inline=False)

    try:
        await logging_channel.send(embed=embed)
    except Exception as e:
        await guild.response.send_message(f"Failed to log the mute. Error: `{e}`", ephemeral=True)

class Mute(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.tree.on_error = self.on_app_command_error

    @app_commands.command(name="mute", description="Mute a user from the server.")
    @app_commands.describe(user = "The user you wish to mute.")
    @app_commands.describe(reason = "Reason for muting the user.")
    @app_commands.describe(duration = "Duration of the mute.")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def mute(self, interaction: discord.Interaction, user: discord.Member, reason: Optional[str], duration: Optional[str] = "7d"):
        if not user.guild_permissions.moderate_members:
            try:
                await mutelog(interaction.guild, user, reason, duration)
                await interaction.response.send_message(f":mute: {user.mention} has been muted for `{reason}`. (Duration: `{duration}`)", ephemeral=True)
                duration = parse_timespan(duration)
                await user.timeout(utils.utcnow() + timedelta(seconds=duration), reason=reason)
            except discord.Forbidden:
                await interaction.response.send_message("I don't have the permissions to mute this member.", ephemeral=True)
            except InvalidTimespan:
                await interaction.response.send_message(f"Duration (`{duration}`) was invalid. (1s, 1m, 1h, 1d)", ephemeral=True)
            except discord.HTTPException as error:
                await interaction.response.send_message(f"An unexpected error occured! Error: `{error}`", ephemeral=True)
        elif user.guild_permissions.moderate_members:
            await interaction.response.send_message("I can't mute this member!", ephemeral=True)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        await asyncio.sleep(1)
        guild = before.guild
        reason = None
        async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.member_update):
            if entry.target.id == before.id:
                reason = entry.reason
                break

        async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.member_update):
            if after.timed_out_until != None:
                await mutelog(guild, before, reason)
                break

    # ERROR HANDLER
    async def on_app_command_error(self, interaction: discord.Interaction, error):
        prfx = (Fore.CYAN + time.strftime("%H:%M:%S UTC", time.gmtime()) + Fore.WHITE + Style.BRIGHT)
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message("This command is on cooldown!", ephemeral=True)
        elif isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("You don't have permission to run this command!", ephemeral=True)
        else:
            await interaction.response.send_message(f"An unexpected error occured! Error: `{error}`", ephemeral=True)
            print(prfx + " Error Handler " + Fore.MAGENTA + f"{error}")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Mute(bot))