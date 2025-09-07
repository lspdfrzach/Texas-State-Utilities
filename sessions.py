import os
import json
import discord
from discord.ext import commands
from dotenv import load_dotenv
from utils import has_any_role_id

load_dotenv()

ADMIN_ROLE_IDS = [int(x.strip()) for x in os.getenv("ADMIN_ROLE_IDS","").split(",") if x.strip().isdigit()]
MOD_ROLE_IDS = [int(x.strip()) for x in os.getenv("MOD_ROLE_IDS","").split(",") if x.strip().isdigit()]
ANNOUNCEMENTS_CHANNEL_ID = int(os.getenv("ANNOUNCEMENTS_CHANNEL_ID","0")) or None

with open("config.json","r",encoding="utf-8") as f:
    CONFIG = json.load(f)

COLOR = CONFIG.get("embed_color", 0xFF7A00)
FOOTER = CONFIG.get("footer_text","")
SERVER_NAME = CONFIG.get("server_name","Server")

def staff_only():
    async def predicate(ctx: commands.Context):
        if ctx.author.guild_permissions.administrator:
            return True
        return has_any_role_id(ctx.author, set(ADMIN_ROLE_IDS + MOD_ROLE_IDS))
    return commands.check(predicate)

class Sessions(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def _announce_channel(self, guild: discord.Guild):
        if ANNOUNCEMENTS_CHANNEL_ID:
            ch = guild.get_channel(ANNOUNCEMENTS_CHANNEL_ID)
            if ch: return ch
        return None

    async def _send(self, ctx: commands.Context, embed: discord.Embed):
        ch = self._announce_channel(ctx.guild)
        if ch:
            await ch.send(embed=embed)
            if ch.id != ctx.channel.id:
                await ctx.reply(f"Posted in {ch.mention}", suppress_embeds=True)
        else:
            await ctx.send(embed=embed)

    @commands.hybrid_command(name="ssu", description="Server Start-Up")
    @staff_only()
    async def ssu(self, ctx: commands.Context):
        embed = discord.Embed(
            title=f"🔶 Server Start-Up",
            description=f"Teaxs State Roleplay has decided to start a roleplay session. Join up for some great roleplays!
            
            **Server Information**
            `-` Owner: SuperNatura1Gaming
            `-` Join Code: txrperlc
            `-` Server Name: Texas State Roleplay | VC Optional",
            color=COLOR
        )
        embed.add_field(name="Start Time",_