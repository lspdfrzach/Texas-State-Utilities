import os
import json
import discord
from discord.ext import commands
from dotenv import load_dotenv
from utils import JSONStore, format_case_embed, has_any_role_id

load_dotenv()

GUILD_ID = int(os.getenv("GUILD_ID", "0")) or None
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID","0")) or None
ADMIN_ROLE_IDS = [int(x.strip()) for x in os.getenv("ADMIN_ROLE_IDS","").split(",") if x.strip().isdigit()]
MOD_ROLE_IDS = [int(x.strip()) for x in os.getenv("MOD_ROLE_IDS","").split(",") if x.strip().isdigit()]

with open("config.json","r",encoding="utf-8") as f:
    CONFIG = json.load(f)

CASE_STORE = JSONStore(CONFIG["case_counter_file"])
WARNS_STORE = JSONStore(CONFIG["warns_file"])

COLOR = CONFIG.get("embed_color", 0xFF7A00)
FOOTER = CONFIG.get("footer_text","")

def is_mod_or_admin():
    async def predicate(ctx: commands.Context):
        if ctx.author.guild_permissions.administrator:
            return True
        return has_any_role_id(ctx.author, set(ADMIN_ROLE_IDS + MOD_ROLE_IDS))
    return commands.check(predicate)

class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _next_case(self) -> int:
        data = await CASE_STORE.read()
        last = data.get("last_case_id", 0) + 1
        data["last_case_id"] = last
        await CASE_STORE.write(data)
        return last

    async def _log(self, guild: discord.Guild, embed: discord.Embed):
        if LOG_CHANNEL_ID:
            channel = guild.get_channel(LOG_CHANNEL_ID)
            if channel:
                await channel.send(embed=embed)

    async def _dm_user(self, user: discord.User, embed: discord.Embed):
        try:
            await user.send(embed=embed)
        except Exception:
            pass

    # ---- WARN ----
    @commands.hybrid_command(name="warn", description="Warn a user with reason.")
    @is_mod_or_admin()
    async def warn(self, ctx: comm