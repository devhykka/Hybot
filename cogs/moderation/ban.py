import discord
import time
import datetime
import json
import mysql.connector
import asyncio
from discord import app_commands
from discord.ext import commands
from typing import Optional
from colorama import Style, Fore

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

async def banlog(guild: discord.Guild, user: discord.Member, reason):
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

    embed = discord.Embed(title="Member Banned",
                          color=discord.Color.red(),
                          timestamp=datetime.datetime.utcnow())
    embed.set_thumbnail(url=user.avatar.url)
    embed.add_field(name="<:id:1264255119147405401> User Info", value=f"Mention: <@{user.id}>\nID: `{user.id}`", inline=True)
    embed.add_field(name="<:crown:1264255117935251557> Staff Info", value=f"Mention: {guild.me.mention}\nID: `{guild.me.id}`", inline=True)
    embed.add_field(name="<:insights:1264255120732983386> Reason", value=f"{reason}", inline=False)

    try:
        await logging_channel.send(embed=embed)
    except Exception as e:
        await guild.response.send_message(f"Failed to log the ban. Error: `{e}`", ephemeral=True)

class Ban(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.tree.on_error = self.on_app_command_error

    @app_commands.command(name="ban", description="Ban a user from the server.")
    @app_commands.describe(user="The user you wish to ban from the server.")
    @app_commands.describe(reason="Reason for banning the user from the server.")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, user: discord.Member, *, reason: Optional[str]):
        try:
            await user.ban(reason=reason)
            await interaction.response.send_message(f":hammer: **{user.name}** has been banned for `{reason}`.", ephemeral=True)
            await banlog(interaction.guild, user, reason)
        except discord.Forbidden:
            await interaction.followup.send("I don't have the permissions to ban this member.", ephemeral=True)
        except discord.HTTPException as error:
            await interaction.followup.send(f"An unexpected error occurred! Error: `{error}`", ephemeral=True)
    
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        await asyncio.sleep(1)
        reason = None
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
            if entry.target.id == user.id:
                reason = entry.reason
                break
        await banlog(guild, user, reason)


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
    await bot.add_cog(Ban(bot))