import discord
import mysql.connector
import json
import random
import string
import requests
from discord import app_commands
from discord.ext import commands

# Load database configuration
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

def generate_verification_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

async def get_minecraft_username(uuid: str) -> str:
    try:
        response = requests.get(f"https://api.mojang.com/user/profile/{uuid}")
        response.raise_for_status()
        data = response.json()
        return data['name']
    except (requests.RequestException, KeyError):
        return "Unknown"

class MinecraftLink(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="link", description="Connect your Minecraft and Discord account.")
    async def link(self, interaction: discord.Interaction):
        code = generate_verification_code()
        database = get_database_connection()
        cursor = database.cursor(dictionary=True)

        check_query = "SELECT * FROM minecraft_link WHERE discord_id = %s"
        cursor.execute(check_query, (str(interaction.user.id),))
        result = cursor.fetchone()

        if result:
            update_query = """
                           UPDATE minecraft_link
                           SET verification_code = %s, minecraft_uuid = '', verified = FALSE
                           WHERE discord_id = %s
                           """
            cursor.execute(update_query, (code, str(interaction.user.id)))
        else:
            # Insert new record
            insert_query = """
                INSERT INTO minecraft_link (discord_id, minecraft_uuid, verification_code, verified)
                VALUES (%s, '', %s, FALSE)
            """
            cursor.execute(insert_query, (str(interaction.user.id), code))

        database.commit()

        embed = discord.Embed(title="Account Verification",
                              description=f"Your account verification code: `{code}`\n\n"
                                          f"**How to verify:**\n"
                                          f"1.) Join `play.aurora-network.cc` (1.21+)\n"
                                          f"2.) Type `/verify <yourcode>` to link your accounts.\n"
                                          f"3.) Go back to Discord and type `/linked` to confirm the link.\n"
                                          f"4.) If successful, you should see an embed with your **username** and **uuid**.",
                              timestamp=discord.utils.utcnow(),
                              color=discord.Color.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="linked", description="Check the Minecraft account linked to a Discord account.")
    async def linked(self, interaction: discord.Interaction, user: discord.User = None):
        user = user or interaction.user
        database = get_database_connection()
        cursor = database.cursor(dictionary=True)

        query = "SELECT minecraft_uuid FROM minecraft_link WHERE discord_id = %s"
        cursor.execute(query, (str(user.id),))
        result = cursor.fetchone()

        if result:
            uuid = result['minecraft_uuid']
            if uuid:
                username = await get_minecraft_username(uuid)
                embed = discord.Embed(title=f"{user.name}'s Information",
                                      description=f"> Discord ID: `{user.id}`\n"
                                                  f"> UUID: `{uuid}`\n"
                                                  f"> Username: `{username}`",
                                      color=discord.Color.blue(),
                                      timestamp=discord.utils.utcnow())
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                embed = discord.Embed(title=f"{user.name} has a pending link.",
                                      color=discord.Color.red(),
                                      timestamp=discord.utils.utcnow())
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(f"{user.name} has no linked Minecraft account.", ephemeral=True)
    
    @app_commands.command(name="linkedlist", description="Get a list of all linked users.")
    async def linkedlist(self, interaction: discord.Interaction):
        database = get_database_connection()
        cursor = database.cursor(dictionary=True)

        query = "SELECT discord_id, minecraft_uuid FROM minecraft_link WHERE verified = TRUE"
        cursor.execute(query)
        results = cursor.fetchall()

        if results:
            linked_users = []
            for result in results:
                user = await self.bot.fetch_user(int(result['discord_id']))
                username = await get_minecraft_username(result['minecraft_uuid'])
                linked_users.append(f"> {user.mention} is linked to `{username}`.")

            response = "\n".join(linked_users)

            embed = discord.Embed(title="Linked Users",
                                  description=f"{response}",
                                  color=discord.Color.blurple(),
                                  timestamp=discord.utils.utcnow())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(title="No users have linked their accounts.",
                                  color=discord.Color.red(),
                                  timestamp=discord.utils.utcnow())
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MinecraftLink(bot))
