import discord
import datetime
import time
from discord import app_commands
from discord.ext import commands
from colorama import Fore, Style
from globalvar import footercontent

class Terms(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.tree.on_error = self.on_app_command_error

    terms_group = app_commands.Group(name="terms", description="Parkour terms and definitions.")

    @terms_group.command(name="oneplayer", description="Get a list of one player parkour terms and definitions.")
    async def oneplayer(self, interaction: discord.Interaction):
        embed = discord.Embed(title="<:one_persons:1255310555024064522> 1 Player Parkour Terms",
                      description="Below is a comprehensive list of 1 player terms, examples are provided to demonstrate how a player might use these terms in-game.\n\n"
                                  "For simplicity, `X` will be used as a number placeholder.\n"
                                  "<:guide:1255319121533472902> **FYI**: `X facing` is wider than `Z facing` on versions before **1.12**.\n"
                                  "<:guide:1255319121533472902> **FYI**: A jump lasts 13 ticks, with 11 ticks in the air.",
                      colour=discord.Color.blue(),
                      timestamp=datetime.datetime.utcnow())
        embed.add_field(name="Terms",
                value="`D1` -> `D12` | Difficulty of a jump, usually based on 'hpk' scaling.\n\n"
                      "`t` | Tick(s), there's 20 ticks in a second.\n"
                      "`bc` | Block ceiling, blocks between floor and ceiling.\n"
                      "`bw`/`fw` | Backward/Forward.\n"
                      "`strafe` | Use 'a' or 'd'.\n"
                      "`neo` | Jumping around a wall or block.\n"
                      "`mm` | Momentum\n\n"
                      "`f` | Is your facing, found in your `F3` screen.\n"
                      "`St` | Tap **movement key** whilst crouching.\n"
                      "`Ut` | Tap **movement key** without crouch.\n"
                      "`Ast` | Tap **movement key** whilst midair and crouching.\n"
                      "`Ust` | Tap **movement key** whilst midair without crouch.\n"
                      "`Swt` | Tap **movement key** whilst blocking with sword/eating gap.",
                inline=False)
        embed.add_field(name="Basic Strats",
                value="`jam` | Press a 'w' and **jump** at the same time.\n"
                      "`hh Xt` | Press a 'w' and **jump** `X` ticks later.\n"
                      "`pessi Xt` | **Jump** on yourself, press 'w' `X` ticks later. (in air)\n"
                      "`pessi` | Hold **jump** then press 'w' before touching the floor. [Requires `2bc`]\n"
                      "`fmm` | Jam fw no sprint, sprint `4t` later. (Max fmm = 1t delay)\n"
                      "`pane fmm` | Pessi `4t`, walk a tick before jumping. (`Xt` pane fmm = `Xt` pessi.)\n"
                      "`a7` | `11t` pessi, press 'w' `1t` before landing.\n"
                      "`c4.5` | `4t` fmm, walk `1t` (`Xt` c4.5 = `Xt` fmm.)",
                inline=False)
        embed.add_field(name="Advanced Strats",
                value="`Mark Xt` | Jam with strafe and add 'w' after `X` tick(s).\n"
                      "`WAD Xt sidestep` | Jump with `WA`/`WD` and switch strafe after `Xt`.\n"
                      "`WAWD Xt sidestep` | Jump with 'w' and strafe after jump tick.\n"
                      "`sidestep` | Pessi, hh or mark with strafe key.\n"
                      "`bwmm` | Jam with 's', walk `1t`, release 's' and press 'w' and 'space'.\n"
                      "`rex bwmm` | bwmm but add strafe upon pressing 'w'.\n"
                      "`reversed rex` | bwmm but add strafe when you jam 's'.\n"
                      "`45s` | Jump, wait `1t`, turn 45° and strafe together.",
                inline=False)
        embed.add_field(name="Some Manual Setups",
                value="`1t 3bc bwmm` | `1ut 1st -> bw`\n"
                      "`2t 3bc bwmm` | `1st -> bw`\n"
                      "`regular rex` | `2st 2ast -> bw`\n"
                      "`regular 45 bwmm` | `f(35)`, `3st 1swt -> bw` + `1swast -> fw`\n"
                      "`2.1 rex` | `f(2.1)`, `1ust 2ast -> bw`",
                inline=False)
        embed.set_footer(text=footercontent["text"], icon_url=footercontent["icon_url"])
        await interaction.response.send_message(embed=embed)

    @terms_group.command(name="twoplayer", description="Get a list of two player parkour terms and definitions.")
    async def twoplayer(self, interaction: discord.Interaction):
        embed = discord.Embed(title="<:two_persons:1255310553929486346> 2 Player Parkour Terms",
                      description="Below is a comprehensive list of 2 player terms, examples are provided to demonstrate how a player might use these terms in-game.",
                      colour=discord.Color.blue(),
                      timestamp=datetime.datetime.utcnow())
        embed.add_field(name="Basic Definitons",
                value="`n` | Short for 'normal', indicating a hit without sprinting or moving.\n"
                      "`s` | Short for 'sprint', indicating a hit with sprinting.\n"
                      "`X` | The number given before `n`/`s` indicates the number of hits.\n"
                      "`3j` | Means jumping twice, then leaping out after landing the third jump.\n"
                      "`2shift` | Means crouching twice, then walking off.\n\n"
                      "`j` | Means jump, hold jump.\n"
                      "`nj` | Means no jump, don't jump.\n\n"
                      "`kb` | Short for 'knockback'.\n"
                      "`pcp` | Short for 'parkour checkpoint'.\n"
                      "`cp` | Short for 'checkpoint'.",
                inline=False)
        embed.add_field(name="Boosts",
                value="`1n` | One normal hit.\n"
                      "`2n` | Two normal hits.\n"
                      "`1s` | One sprint hit.\n"
                      "`2s` | Two sprint hits.\n"
                      "`vn` | Hit the player once, turn fast then hit a second time.\n"
                      "`3jw` | Jump twice, then walk out after landing the third jump.\n"
                      "`3js` | Jump twice, then sprint out after landing the third jump.",
                inline=False)
        embed.add_field(name="Examples",
                value="`3jw 2n` | Do a '3jw', and get your partner to '2n' you.\n"
                      "`2s nj` | Don't jump, get your partner to '2s' you.\n"
                      "`3js 1s` | Do a '3js', and get your partner to '1s' you.",
                inline=False)
        embed.set_footer(text=footercontent["text"], icon_url=footercontent["icon_url"])
        await interaction.response.send_message(embed=embed)

    # ERROR HANDLER
    async def on_app_command_error(self, interaction: discord.Interaction, error):
        prfx = (Fore.CYAN + time.strftime("%H:%M:%S UTC", time.gmtime()) + Fore.WHITE + Style.BRIGHT)
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("You don't have permission to run this command!", ephemeral=True)
        else:
            await interaction.response.send_message(f"An unexpected error occured! Error: `{error}`", ephemeral=True)
            print(prfx + " Error Handler " + Fore.MAGENTA + f"{error}")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Terms(bot))