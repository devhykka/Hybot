import discord
import mysql.connector
import json
import io
import requests
import time
from colorama import Fore, Style
from easy_pil import Editor, load_image_async, Font
from discord.ext import commands

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

async def get_welcomer_config(guild_id):
    database = get_database_connection()
    cursor = database.cursor(dictionary=True)
    query = "SELECT `guild_id`, `channel_id`, `message_content`, `message_banner` FROM `welcomer` WHERE `guild_id` = %s"
    cursor.execute(query, (guild_id,))
    result = cursor.fetchone()
    database.close()
    return result

async def load_welcome_banner(url):
    default_banner_path = "welcome_banner.png"
    try:
        if url:
            response = requests.get(url)
            response.raise_for_status()
            image_bytes = io.BytesIO(response.content)
            return Editor(image_bytes).resize((1920, 1080))
        else:
            return Editor(default_banner_path).resize((1920, 1080))
    except Exception as error:
        prfx = (Fore.CYAN + time.strftime("%H:%M:%S UTC", time.gmtime()) + Fore.WHITE + Style.BRIGHT)
        print(prfx + " Error Handler " + Fore.MAGENTA + f"{error}")
        return Editor(default_banner_path).resize((1920, 1080))

class Welcome(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        config = await get_welcomer_config(member.guild.id)
        
        if not config or not config['channel_id']:
            return

        welcome_channel_id = int(config['channel_id'])
        welcome_channel = discord.utils.get(member.guild.text_channels, id=welcome_channel_id)
        welcome_banner_url = config.get('message_banner', None)

        message_content = config.get('message_content') or f"{member.name} is member #{member.guild.member_count}!"
        message_content = message_content.replace('{member.name}', member.name)
        message_content = message_content.replace('{member.count}', f"{member.guild.member_count}")

        background = await load_welcome_banner(welcome_banner_url)

        avatar_image = await load_image_async(str(member.avatar.url))
        avatar = Editor(avatar_image).resize((250, 250)).circle_image()

        font_big = Font.poppins(size=90, variant="bold")
        font_small = Font.poppins(size=60, variant="bold")
        
        background.paste(avatar, (835, 340))
        background.ellipse((835, 340), 250, 250, outline="white", stroke_width=5)
        background.text((960, 620), f"Welcome to {member.guild.name}!", color="white", font=font_big, align="center")
        background.text((960, 740), f"{message_content}", color="white", font=font_small, align="center")

        edited_image_bytes = io.BytesIO()
        background.save(edited_image_bytes, "png")
        edited_image_bytes.seek(0)

        file = discord.File(fp=edited_image_bytes, filename="welcome_banner.png")
        await welcome_channel.send(f"Welcome {member.mention} to {member.guild.name}!", file=file)

async def setup(bot):
    await bot.add_cog(Welcome(bot))