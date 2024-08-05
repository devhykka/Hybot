import discord
import datetime
import mysql.connector
import time
import asyncio
import json
from discord import app_commands
from discord.ext import commands
from typing import Optional
from colorama import Fore, Style
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

def timestamp_converter(dt: datetime.datetime):
     return f"<t:{int(dt.timestamp())}>"

async def get_ticket_config(guild_id):
        database = get_database_connection()
        cursor = database.cursor(dictionary=True)
        query = "SELECT `staff_role_id`, `ticket_category_id`, `logs_channel_id` FROM `tickets_config` WHERE `guild_id` = %s"
        cursor.execute(query, (guild_id,))
        result = cursor.fetchone()
        database.close()
        return result

async def ticketlog(interaction:discord.Interaction, reason, ticket_name):
        ticket_deletion_date = timestamp_converter(datetime.datetime.utcnow())
        config = await get_ticket_config(interaction.guild.id)
        logging_channel_id = config['logs_channel_id']
        logging_channel = discord.utils.get(interaction.guild.text_channels, id=logging_channel_id)
        channel_topic = interaction.channel.topic

        if logging_channel is None:
            await interaction.response.send_message("Logging channel not found!", ephemeral=True)
            return

        if channel_topic is None:
             ticket_creation_date = "`unknown`"
        else:
            ticket_creation_date = timestamp_converter(datetime.datetime.fromisoformat(channel_topic))

        embed = discord.Embed(title="Ticket Closed",
                              color=discord.Color.red(),
                              timestamp= datetime.datetime.utcnow())
        embed.add_field(name="<:guide:1255319121533472902> Ticket Name", value=f"{ticket_name}", inline=False)
        embed.add_field(name="<:one_persons:1255310555024064522> Closed By", value=f"{interaction.user.mention}", inline=True)
        embed.add_field(name="<:join:1255310294776025190> Open Time", value=f"{ticket_creation_date}", inline=True)
        embed.add_field(name="<:leave:1255310296390701136> Close Time", value=f"{ticket_deletion_date}", inline=True)
        embed.add_field(name="<:error:1255309964944085042> Reason", value=f"{reason}", inline=False)
        await logging_channel.send(embed=embed)

class Tickets(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.tree.on_error = self.on_app_command_error
    
    @commands.command(name="ticketpanel")
    async def panel(self, ctx):
        embed = discord.Embed(
            title="📩 Open a ticket",
            description="Open a ticket to have a direct channel to talk to staff.\n\n"
                        "Click a button below to open a new ticket, please open the correct ticket regarding your issue."
                        "For issues with the payments or the payment gateway on the store, please open a `Payment Support` ticket.",
            colour=discord.Color.blurple(),
            timestamp=datetime.datetime.utcnow())
        embed.set_image(url="https://images-ext-1.discordapp.net/external/nXZGBbk7B22zj5sBn0wB5anrcz-bH57y2cjGrKpbn2U/https/assets-global.website-files.com/5f9072399b2640f14d6a2bf4/64af3aac29866b3f86f1c648_Products%2520%2526%2520Features%2520-%25202.png?format=webp&quality=lossless&width=1440&height=576")
        embed.set_footer(icon_url="https://i.postimg.cc/Y9Tgwwbb/eb8-logo.png")
        
        await ctx.send(embed=embed, view=TicketButton())
        pass

    @app_commands.command(name="ticketclose", description="Closes the current ticket.")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def closeticket(self, interaction: discord.Interaction, reason: Optional[str]):
            if not interaction.channel.name.startswith("ticket-"):
                await interaction.response.send_message("This command can only be used in tickets!", ephemeral=True)
            else:
                try:
                    reason = reason or "No reason given."
                    ticket_name = interaction.channel.name
                    await interaction.response.send_message(f"Closing ticket in 3 seconds. Reason: `{reason}`", ephemeral=True)
                    await ticketlog(interaction, reason, ticket_name)
                    await asyncio.sleep(3)
                    await interaction.channel.delete()
                except discord.Forbidden:
                    await interaction.followup.send("I don't have permission to delete this channel.", ephemeral=True)
                except discord.HTTPException as error:
                    await interaction.followup.send(f"An error occured! `{error}", ephemeral=True)

    @app_commands.command(name="ticketadd", description="Adds a user or role to the current ticket.")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def addticket(self, interaction: discord.Interaction, user: Optional[discord.Member] = None, role: Optional[discord.Role] = None):
        if not interaction.channel.name.startswith("ticket-"):
            await interaction.response.send_message("This command can only be used in tickets!", ephemeral=True)
            return
        
        if user is None and role is None:
            await interaction.response.send_message("Please specify a user or role to add to the ticket.", ephemeral=True)
            return

        try:
            if not interaction.channel.permissions_for(interaction.guild.me).manage_channels:
                await interaction.response.send_message("I don't have permission to manage this channel.", ephemeral=True)
                return

            overwrite = discord.PermissionOverwrite(read_messages=True, send_messages=True)
            
            if user is not None:
                await interaction.channel.set_permissions(user, overwrite=overwrite)
                await interaction.response.send_message(f"{user.mention} has been added to the ticket.")

            if role is not None:
                await interaction.channel.set_permissions(role, overwrite=overwrite)
                await interaction.response.send_message(f"{role.mention} has been added to the ticket.")
        
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to add this user or role to the ticket.", ephemeral=True)
        
        except discord.HTTPException as error:
            await interaction.response.send_message(f"An error occurred: `{error}`", ephemeral=True)
   
    @app_commands.command(name="ticketremove", description="Remove a user from the current ticket.")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def removeticket(self, interaction: discord.Interaction, user: discord.Member):
        if not interaction.channel.name.startswith("ticket-"):
            await interaction.response.send_message("This command can only be used in tickets!", ephemeral=True)
            return
        
        try:
            if not interaction.channel.permissions_for(interaction.guild.me).manage_channels:
                await interaction.response.send_message("I don't have permission to manage this channel.", ephemeral=True)
                return
            
            overwrite = discord.PermissionOverwrite(read_messages=False, send_messages=False)
            await interaction.channel.set_permissions(user, overwrite=overwrite)
            await interaction.response.send_message(f"{user.mention} has been removed from the ticket.")
        
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to add this user to the ticket.", ephemeral=True)
        
        except discord.HTTPException as error:
            await interaction.response.send_message(f"An error occurred: `{error}`", ephemeral=True)

    # ERROR HANDLER
    async def on_app_command_error(self, interaction: discord.Interaction, error):
        prfx = (Fore.CYAN + time.strftime("%H:%M:%S UTC", time.gmtime()) + Fore.WHITE + Style.BRIGHT)
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("You don't have permission to run this command!", ephemeral=True)
        else:
            await interaction.response.send_message(f"An unexpected error occured! Error: `{error}`", ephemeral=True)
            print(prfx + " Error Handler " + Fore.MAGENTA + f"{error}")
        
class TicketButton(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    # Blurple "Open Ticket" button on panel.
    @discord.ui.button(label="Open a ticket!", emoji="📩", style=discord.ButtonStyle.blurple, custom_id="openticket")
    async def button(self, interaction: discord.Interaction, Button: discord.ui.Button):
        await interaction.response.defer()
        await self.createticket(interaction)

    async def createticket(self, interaction: discord.Interaction):
        config = await get_ticket_config(interaction.guild.id)
        if not config:
            await interaction.followup.send("Ticket configuration not found for this guild.", ephemeral=True)
            return

        staffteam = discord.utils.get(interaction.guild.roles, id=config['staff_role_id'])
        if not staffteam:
            await interaction.followup.send("Staff role not found.", ephemeral=True)
            return
        
        category = discord.utils.get(interaction.guild.categories, id=config['ticket_category_id'])
        if not category:
            await interaction.followup.send("Ticket category not found.", ephemeral=True)
            return

        channeloverwrites = {interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
                             staffteam: discord.PermissionOverwrite(view_channel=True, send_messages=True),
                             interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False)}
        
        channel = await interaction.guild.create_text_channel(name=f"ticket-{interaction.user.name}",
                                                              topic=f"{datetime.datetime.utcnow()}",
                                                              overwrites=channeloverwrites, 
                                                              category=category)
        tag = await channel.send(staffteam.mention)
        await tag.delete()

        # Sends embed in the panel channel.
        embed = discord.Embed(title="Ticket",
                              description=f"Opened a new ticket: {channel.mention}",
                              color=discord.Color.green(),
                              timestamp=datetime.datetime.utcnow())
        embed.set_footer(text=footercontent["text"], icon_url=footercontent["icon_url"])
        await interaction.followup.send(embed=embed, ephemeral=True)

        # Sends embed in the ticket channel.
        embed = discord.Embed(title="📩 Ticket",
                              description="Thank you for opening a ticket! A member of staff will be with you shortly.\n\n"
                                          "In the meantime, please explain why you opened a ticket and give any necessary details.", 
                              colour=discord.Color.blurple(),
                              timestamp=datetime.datetime.utcnow())
        embed.set_image(url=images["ticketsbanner"])
        embed.set_footer(text=footercontent["text"], icon_url=footercontent["icon_url"])
        await channel.send(embed=embed, view=RequestCloseTicketButton())

class RequestCloseTicketButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Request", emoji="🔒", style=discord.ButtonStyle.danger, custom_id="closerequest")
    async def closerequest(self, interaction: discord.Interaction, button: discord.ui.Button):
            if not interaction.channel.name.startswith("ticket-"):
                await interaction.response.send_message("This command can only be used in tickets!", ephemeral=True)
            else:
                embed = discord.Embed(title="Confirm Close",
                                      description=f"{interaction.user.mention} has requested to close the ticket!",
                                      color= discord.Color.green(),
                                      timestamp= datetime.datetime.utcnow())
                await interaction.response.send_message(embed= embed, view=ConfirmTicketCloseButton())

class ConfirmTicketCloseButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Confirm Close", emoji="✔", style=discord.ButtonStyle.green, custom_id="confirmcloseticket")
    async def confirmcloseticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.guild.get_member(interaction.user.id)
        if user.guild_permissions.manage_channels:
            try:
                reason = "No reason given."
                ticket_name = interaction.channel.name
                await interaction.response.send_message(f"Closing ticket in 3 seconds...", ephemeral=True)
                await ticketlog(interaction, reason, ticket_name)
                await asyncio.sleep(3)
                await interaction.channel.delete()
            except discord.Forbidden:
                await interaction.followup.send("I don't have permission to delete this channel.", ephemeral=True)
            except discord.HTTPException as error:
                await interaction.followup.send(f"An error occured! `{error}", ephemeral=True)
        else:
            await interaction.response.send_message("You do not have permission to delete this channel.", ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Tickets(bot))
    bot.add_view(ConfirmTicketCloseButton())
    bot.add_view(TicketButton())
    bot.add_view(RequestCloseTicketButton()) 