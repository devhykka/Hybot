import discord
import datetime
import mysql.connector
import time
import humanfriendly
import random
import json
from humanfriendly import parse_timespan
from discord import app_commands, ui, utils
from discord.ext import commands, tasks
from colorama import Fore, Style
from typing import Optional

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

def timestamp_converter(dt: datetime.datetime):
    return f"<t:{int(dt.timestamp())}:R>"

def bonus_timestamp_converter(dt: datetime.datetime):
    return f"<t:{int(dt.timestamp())}:f>"

async def validate_duration_input(interaction: discord.Interaction, duration):
    try:
        parsed_duration = parse_timespan(duration)
        if parsed_duration <= 0:
            await interaction.response.send_message("Duration can't be `< 1`! Try: `7d`, `45m`, `18h`.", ephemeral=True)
            return False, None
        return True, parsed_duration
    except ValueError:
        await interaction.response.send_message("Duration isn't valid! Try: `6d`, `10m`, `2h`.", ephemeral=True)
        return False, None
    except humanfriendly.InvalidTimespan as error:
        await interaction.response.send_message("Duration isn't valid! Try: `1d`, `30m`, `6h`.", ephemeral=True)
        return False, None

async def get_giveaway(guild_id, message_id):
    database = get_database_connection()
    
    cursor = database.cursor(dictionary=True)
    query = "SELECT `channel_id`, `message_id`, `end_time`, `prize`, `description`, `participants`, `winners`, `host` FROM `giveaways` WHERE `guild_id`=%s AND `message_id`=%s"
    cursor.execute(query, (guild_id, message_id))
    result = cursor.fetchone()
    database.close()
    return result

class Giveaways(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.tree.on_error = self.on_app_command_error
        self.check_giveaways.start()

    giveaway_group = app_commands.Group(name="giveaway", description="Giveaway commands.")

    @giveaway_group.command(name="create", description="Create a giveaway.")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def create_giveaway(self, interaction: discord.Interaction):
        await interaction.response.send_modal(GiveawayModal())

    @giveaway_group.command(name="reroll", description="Reroll a giveaway.")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.describe(message_id = "The ID of the giveaway you want to reroll.")
    @app_commands.describe(count = "The number of users to reroll.")
    async def reroll_giveaway(self, interaction: discord.Interaction, message_id: str, count: Optional[int] = None):
        await interaction.response.defer(ephemeral=True)

        if not message_id.isdigit():
            await interaction.response.send_message("Please provide a valid message ID.", ephemeral=True)
            return

        message_id = int(message_id)

        database = get_database_connection()
        cursor = database.cursor(dictionary=True)
        query = "SELECT `guild_id`, `channel_id`, `message_id`, `end_time`, `prize`, `description`, `participants`, `winners`, `host` FROM `giveaways` WHERE `guild_id`=%s AND `message_id`=%s"
        cursor.execute(query, (interaction.guild.id, message_id))
        giveaway = cursor.fetchone()
        database.close()

        if not giveaway:
            await interaction.followup.send("Giveaway not found!", ephemeral=True)
            return
        
        if count is None:
            count = int(giveaway['winners'])

        participants = giveaway['participants'].split(",") if giveaway['participants'] else []
        if not participants:
            await interaction.followup.send("No participants to reroll!", ephemeral=True)
            return

        winners = random.sample(participants, min(count, len(participants)))
        winners_mentions = ", ".join([f"<@{winner}>" for winner in winners])

        guild = self.bot.get_guild(giveaway['guild_id'])
        if not guild:
            await interaction.followup.send("Guild not found!", ephemeral=True)
            return

        channel = guild.get_channel(giveaway['channel_id'])
        if not channel:
            await interaction.followup.send("Channel not found!", ephemeral=True)
            return
        
        await channel.send(f":tada: Congratulations {winners_mentions}! You won the reroll for **{giveaway['prize']}**!")
        await interaction.followup.send("Rerolled the giveaway successfully!", ephemeral=True)

    @giveaway_group.command(name="delete", description="Delete a giveaway.")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def delete_giveaway(self, interaction: discord.Interaction, message_id: str):
        if not message_id.isdigit():
            await interaction.response.send_message("Please provide a valid message ID.", ephemeral=True)
            return

        message_id = int(message_id)
        giveaway = await get_giveaway(interaction.guild.id, message_id)
        if not giveaway:
            await interaction.response.send_message("Giveaway not found!", ephemeral=True)
            return

        database = get_database_connection()
        cursor = database.cursor()
        query = "DELETE FROM `giveaways` WHERE `message_id`=%s"
        cursor.execute(query, (message_id,))
        database.close()

        await interaction.response.send_message("Giveaway deleted successfully!", ephemeral=True)

    @tasks.loop(seconds=10)
    async def check_giveaways(self):
        database = get_database_connection()
        
        cursor = database.cursor(dictionary=True)
        query = "SELECT `guild_id`, `channel_id`, `message_id`, `end_time`, `prize`, `description`, `participants`, `winners`, `host`, `ended` FROM `giveaways` WHERE `end_time` <= NOW()"
        cursor.execute(query)
        giveaways = cursor.fetchall()

        for giveaway in giveaways:
            if not giveaway['ended']:
                await self.end_giveaway(giveaway)

        database.close()

    async def end_giveaway(self, giveaway):
        guild = self.bot.get_guild(giveaway['guild_id'])
        if guild:
            channel = guild.get_channel(giveaway['channel_id'])
            if channel:
                message = await channel.fetch_message(giveaway['message_id'])
                if message:
                    participants = giveaway['participants'].split(",") if giveaway['participants'] else []
                    if participants:
                        winners = random.sample(participants, min(int(giveaway['winners']), len(participants)))
                        winners_mentions = ", ".join([f"<@{winner}>" for winner in winners])
                        embed = discord.Embed(title=f"{giveaway['prize']}",
                                              description=f"{giveaway['description']}\n\n"
                                                          f"Ended: {timestamp_converter(utils.utcnow())}\n"
                                                          f"Hosted by: <@{giveaway['host']}>\n"
                                                          f"Entries: {len(participants)}\n"
                                                          f"Winners: {winners_mentions}\n",
                                              color=0x2f3136,
                                              timestamp=datetime.datetime.utcnow())
                        await message.edit(embed=embed, view=None)
                        await channel.send(f":tada: Congratulations {winners_mentions}! You won the giveaway for **{giveaway['prize']}**!")
                    else:
                        await channel.send(f"The giveaway for **{giveaway['prize']}** ended with no participants.")
                    
                    database = get_database_connection()
                    cursor = database.cursor()
                    query = "UPDATE `giveaways` SET `ended`=TRUE WHERE `message_id`=%s"
                    cursor.execute(query, (giveaway['message_id'],))
                    database.close()

    # ERROR HANDLER
    async def on_app_command_error(self, interaction: discord.Interaction, error):
        prfx = (Fore.CYAN + time.strftime("%H:%M:%S UTC", time.gmtime()) + Fore.WHITE + Style.BRIGHT)
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("You don't have permission to run this command!", ephemeral=True)
        else:
            await interaction.response.send_message(f"An unexpected error occurred! Error: `{error}`", ephemeral=True)
            print(prfx + " Error Handler " + Fore.MAGENTA + f"{error}")

class GiveawayModal(ui.Modal, title="Host Giveaway"):
    duration = ui.TextInput(label="Giveaway Duration", placeholder="E.g. 1m, 6h, 7d", style=discord.TextStyle.short, required=True)
    winners = ui.TextInput(label="Number of Winners", default="1", style=discord.TextStyle.short, required=True)
    prize = ui.TextInput(label="Prize", style=discord.TextStyle.short, required=True)
    description = ui.TextInput(label="Description", style=discord.TextStyle.long, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        valid, parsed_duration = await validate_duration_input(interaction, self.duration.value)
        if not valid:
            return
        
        end_time = utils.utcnow() + datetime.timedelta(seconds=parsed_duration)
        winners = self.winners.value
        prize = self.prize.value
        description = self.description.value if self.description.value else "No description given."
        participants = ""

        embed = discord.Embed(
            title=f"{prize}",
            description=f"{description}\n\n"
                        f"Ends: {timestamp_converter(end_time)} ({bonus_timestamp_converter(end_time)})\n"
                        f"Hosted by: {interaction.user.mention}\n"
                        f"Winners: {winners}",
            timestamp=datetime.datetime.utcnow(),
            color=discord.Color.blue()
        )
        
        view = JoinGiveawayView(
            guild_id=interaction.guild.id, 
            channel_id=interaction.channel.id,
            message_id=None,
            message= None, 
            end_time=end_time, 
            prize=prize, 
            description=description,
            participants=participants, 
            winners=winners,
            host=interaction.user.id
        )
        
        await interaction.response.send_message(embed=embed, view=view)
        message = await interaction.original_response()
        view.message = message #pass the message there
        view.message_id = message.id  # Update the message_id in the view

        database = get_database_connection()
        
        query = ("INSERT INTO `giveaways` (`guild_id`, `channel_id`, `message_id`, `end_time`, `prize`, `description`, `participants`, `winners`, `host`)"
                 " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                 " ON DUPLICATE KEY UPDATE "
                 "`channel_id` = VALUES(`channel_id`), "
                 "`message_id` = VALUES(`message_id`), "
                 "`end_time` = VALUES(`end_time`), "
                 "`prize` = VALUES(`prize`), "
                 "`description` = VALUES(`description`), "
                 "`participants` = VALUES(`participants`), "
                 "`winners` = VALUES(`winners`), "
                 "`host` = VALUES(`host`)")
        values = (
            interaction.guild.id,
            interaction.channel.id,
            message.id,
            end_time,
            prize,
            description,
            participants,
            winners,
            interaction.user.id
        )

        cursor = database.cursor(dictionary=True)
        try:
            cursor.execute(query, values)
            await interaction.followup.send("Giveaway created successfully!", ephemeral=True)
        except mysql.connector.Error as error:
            await interaction.followup.send(f"Error saving giveaway to database, delete embed and try again. Error: `{error}`", ephemeral=True)
        finally:
            database.close()

class JoinGiveawayView(discord.ui.View):
    def __init__(self, guild_id, channel_id, message_id, message, end_time, prize, description, participants, winners, host):
        super().__init__(timeout=None)
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.message_id = message_id
        self.message = None
        self.end_time = end_time
        self.prize = prize
        self.description = description
        self.participants = participants
        self.winners = winners
        self.host = host

    @discord.ui.button(label="Join Giveaway", emoji="🎉", style=discord.ButtonStyle.blurple, custom_id="joingiveaway")
    async def giveaway_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await self.join_giveaway(interaction)

    async def join_giveaway(self, interaction: discord.Interaction):
        giveaway = await get_giveaway(self.guild_id, self.message_id)
        participants = giveaway["participants"].split(",") if giveaway["participants"] else []

        if str(interaction.user.id) in participants:
            await interaction.followup.send("You are already participating in this giveaway!", ephemeral=True)
            return

        participants.append(str(interaction.user.id))
        participants_str = ",".join(participants)

        database = get_database_connection()
        
        query = "UPDATE `giveaways` SET `participants`=%s WHERE `message_id`=%s"
        cursor = database.cursor()
        cursor.execute(query, (participants_str, self.message_id))
        database.close()

        embed = discord.Embed(
            title=f"{self.prize}",
            description=f"{self.description}\n\n"
                        f"Ends: {timestamp_converter(self.end_time)} ({bonus_timestamp_converter(self.end_time)})\n"
                        f"Hosted by: <@{self.host}>\n"
                        f"Winners: {self.winners}\n"
                        f"Participants: {len(participants)}",
            timestamp=datetime.datetime.utcnow(),
            color=discord.Color.blue()
        )
        await self.message.edit(embed=embed, view=self)

        await interaction.followup.send("You have successfully joined the giveaway!", ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    database = get_database_connection()
    
    cursor = database.cursor(dictionary=True)
    query = "SELECT `guild_id`, `channel_id`, `message_id`, `end_time`, `prize`, `description`, `participants`, `winners`, `host` FROM `giveaways`"
    cursor.execute(query)
    giveaways = cursor.fetchall()
    database.close()

    for giveaway in giveaways:
        bot.add_view(JoinGiveawayView(
            guild_id=giveaway["guild_id"],
            channel_id=giveaway["channel_id"],
            message_id=giveaway["message_id"],
            message = None,
            end_time=giveaway["end_time"],
            prize=giveaway["prize"],
            description=giveaway["description"],
            participants=giveaway["participants"],
            winners=giveaway["winners"],
            host=giveaway["host"]))

    await bot.add_cog(Giveaways(bot))
