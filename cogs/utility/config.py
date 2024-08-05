import discord
import datetime
import mysql.connector
import time
import json
from typing import Optional
from discord import app_commands
from discord.ext import commands
from colorama import Fore, Style
from cogs.utility.tickets import Tickets, TicketButton
from globalvar import footercontent, images

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

class Config(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.tree = bot.tree
        self.tickets = Tickets(bot)
        self.bot.tree.on_error = self.on_app_command_error

    config_group = app_commands.Group(name="config", description="Server configuration.")

    @config_group.command(name="tickets", description="Tickets configuration.")
    @app_commands.checks.has_permissions(administrator=True)
    async def tickets(self, interaction: discord.Interaction, panel_channel: discord.TextChannel, 
                                                              staff_role: discord.Role, 
                                                              ticket_category: discord.CategoryChannel, 
                                                              logs_channel: discord.TextChannel):
        database = get_database_connection()
        cursor = database.cursor(dictionary=True)
        query = ("INSERT INTO `tickets_config`(`guild_id`, `panel_channel_id`, `staff_role_id`, `ticket_category_id`, `logs_channel_id`)"
                 "VALUES (%s, %s, %s, %s, %s)"
                 "ON DUPLICATE KEY UPDATE"
                 "`panel_channel_id` = VALUES(`panel_channel_id`), "
                 "`staff_role_id` = VALUES(`staff_role_id`), "
                 "`ticket_category_id` = VALUES(`ticket_category_id`), "
                 "`logs_channel_id` = VALUES(`logs_channel_id`)")
        values = (interaction.guild.id,
                  panel_channel.id,
                  staff_role.id,
                  ticket_category.id,
                  logs_channel.id)
        
        try:
            cursor.execute(query, values)
            await interaction.response.send_message("Configuration saved successfully!", ephemeral=True)
        except mysql.connector.Error as error:
            await interaction.response.send_message(f"Error saving configuration. `{error}`", ephemeral=True)
        finally:
            database.close()
        
        embed = discord.Embed(
            title="📩 Open a ticket",
            description="Open a ticket to have a direct channel to talk to staff.\n\n"
                        "Click the button below to open a new ticket, please avoid opening more than one ticket at a time though.",
            colour=discord.Color.blurple(),
            timestamp=datetime.datetime.utcnow())
        embed.set_image(url=images["ticketspanel"])
        embed.set_footer(text=footercontent["text"], icon_url=footercontent["icon_url"])
        
        await panel_channel.send(embed=embed, view=TicketButton())

    @config_group.command(name="levels", description="Levels configuration.")
    @app_commands.checks.has_permissions(administrator=True)
    async def levels(self, interaction: discord.Interaction):
        await interaction.response.send_message("Levels Config")

    @config_group.command(name="welcome", description="Welcome banner configuration.")
    @app_commands.checks.has_permissions(administrator=True)
    async def welcome(self, interaction: discord.Interaction, welcome_channel: discord.TextChannel, message_content: Optional[str], message_banner: Optional[str]):
        database = get_database_connection()
        cursor = database.cursor(dictionary=True)

        try:
            query = ("INSERT INTO welcomer(guild_id, channel_id, message_content, message_banner)"
                     "VALUES (%s, %s, %s, %s)"
                     "ON DUPLICATE KEY UPDATE "
                     "channel_id = VALUES(channel_id), "
                     "message_content = VALUES(message_content), "
                     "message_banner = VALUES(message_banner)")
        
            if message_content is None:
                message_content = None
        
            if message_banner is None:
                message_banner = None
        
            values = (interaction.guild.id,
                  welcome_channel.id,
                  message_content,
                  message_banner)
        
            cursor.execute(query, values)
            await interaction.response.send_message("Configuration saved successfully!", ephemeral=True)
        except mysql.connector.Error as error:
            await interaction.response.send_message(f"Error saving configuration. {error}", ephemeral=True)
        finally:
            cursor.close()
            database.close()
    
    @config_group.command(name="autoroles", description="Autoroles configuration")
    @app_commands.checks.has_permissions(administrator=True)
    async def autoroles(self, interaction: discord.Interaction):
        await interaction.response.send_message("Autoroles Config")

    @config_group.command(name="logging", description="Logging configuration.")
    @app_commands.checks.has_permissions(administrator=True)
    async def logging(self, interaction: discord.Interaction, logging_channel: discord.TextChannel):
        database = get_database_connection()
        cursor = database.cursor(dictionary=True)

        try:
            query = ("INSERT INTO guild_configs(guild_id, logging_channel)"
                     "VALUES (%s, %s)"
                     "ON DUPLICATE KEY UPDATE "
                     "logging_channel = VALUES(logging_channel)")
            
            values = (interaction.guild.id,
                      logging_channel.id)
            
            cursor.execute(query, values)
            await interaction.response.send_message("Configuration saved successfully!", ephemeral=True)
        except mysql.connector.Error as error:
            await interaction.response.send_message(f"Error saving configuration. `{error}`", ephemeral=True)

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
    await bot.add_cog(Config(bot))