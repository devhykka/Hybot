import discord
import time
import platform
import os
from discord.ext import commands
from colorama import Fore, Style
from dotenv import load_dotenv
from typing import Final

prfx = (Fore.CYAN + time.strftime("%H:%M:%S UTC", time.gmtime()) + Fore.WHITE + Style.BRIGHT)

class Bot(commands.Bot):
    def __init__(self):
        activity = discord.Activity(type=discord.ActivityType.listening, name="/help | by @.hykka")
        super().__init__(command_prefix="h!", intents=discord.Intents().all(), activity=activity, status=discord.Status.online, help_command=None)

    async def on_ready(self):
        print(Fore.BLUE + " ____   ____ _______     ____  _   _ _      _____ _   _ ______ ")
        print("|  _ \ / __ \__   __|   / __ \| \ | | |    |_   _| \ | |  ____|")
        print("| |_) | |  | | | |     | |  | |  \| | |      | | |  \| | |__   ")
        print("|  _ <| |  | | | |     | |  | | . ` | |      | | | . ` |  __|  ")
        print("| |_) | |__| | | |     | |__| | |\  | |____ _| |_| |\  | |____   _")
        print("|____/ \____/  |_|      \____/|_| \_|______|_____|_| \_|______| |_|")
        print(" ")
        print(prfx + " Logged in as " + Fore.MAGENTA + bot.user.name)
        print(prfx + " Bot ID " + Fore.MAGENTA + str(bot.user.id))
        print(prfx + " Discord Version " + Fore.MAGENTA + discord.__version__)
        print(prfx + " Python Version " + Fore.MAGENTA + str(platform.python_version()))
        print(prfx + " Bot Latency " + Fore.MAGENTA + f"{round(bot.latency*1000)}ms")
        synced = await self.tree.sync()
        print(prfx + " Slash Commands " + Fore.MAGENTA + str(len(synced)) + " Commands Synced")
        print(" ")

    async def setup_hook(self):
        for filename in os.listdir('cogs/moderation'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.moderation.{filename[:-3]}')
                print(prfx + " Cogs Extensions " + Fore.MAGENTA + f"Loaded extension '{filename}'")

        for filename in os.listdir('cogs/other'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.other.{filename[:-3]}')
                print(prfx + " Cogs Extensions " + Fore.MAGENTA + f"Loaded extension '{filename}'")

        for filename in os.listdir('cogs/utility'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.utility.{filename[:-3]}')
                print(prfx + " Cogs Extensions " + Fore.MAGENTA + f"Loaded extension '{filename}'")

        for filename in os.listdir('cogs/control'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.control.{filename[:-3]}')
                print(prfx + " Cogs Extensions " + Fore.MAGENTA + f"Loaded extension '{filename}'")
              
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')
bot = Bot()
bot.run(TOKEN)