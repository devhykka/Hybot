import discord
import time
import mysql.connector
import json
from discord.ext import commands
from colorama import Style, Fore

prfx = (Fore.CYAN + time.strftime("%H:%M:%S UTC", time.gmtime()) + Fore.WHITE + Style.BRIGHT)


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

async def delete_guild_config(guild_id):
    try:
        with get_database_connection() as database:
            with database.cursor() as cursor:
                query = "DELETE FROM `tickets_config` WHERE `guild_id` = %s"
                cursor.execute(query, (guild_id))
                query = "DELETE FROM `giveaways` WHERE `guild_id` = %s"
                cursor.execute(query, (guild_id))
                query = "DELETE FROM `guild_configs` WHERE `guild_id` = %s"
                cursor.execute(query, (guild_id))
    except mysql.connector.Error as err:
        print(f"Error: {err}")

class dbHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.tree.on_error = self.on_app_command_error

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await delete_guild_config(guild.id)
        print(prfx + " dbHandler " + Fore.MAGENTA + f"Removed configuration from {guild.name} (ID: {guild.id})")

    # ERROR HANDLER
    async def on_app_command_error(self, interaction: discord.Interaction, error):
        prfx = (Fore.CYAN + time.strftime("%H:%M:%S UTC", time.gmtime()) + Fore.WHITE + Style.BRIGHT)
        print(prfx + " Error Handler " + Fore.MAGENTA + f"{error}")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(dbHandler(bot))