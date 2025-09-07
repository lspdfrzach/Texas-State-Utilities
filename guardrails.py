import os
import json
import discord
from discord.ext import commands
from dotenv import load_dotenv
from utils import JSONStore, format_case_embed

load_dotenv()

LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID","0")) or None
PROTECTED_ROLE_ID = int(os.getenv("PROTECTED_ROLE_ID","0")) or None

with open("config.json","r",encoding="utf-8") as f:
    CONFIG = json.load(f)

COLOR = CONFIG.get("embed_color", 0xFF7A00)
FOOTER = CONFIG.get("footer_text","")

CASE_STORE = JSONStore(CONFIG["case_counter_file"])
WARNS_STORE = JSONStore(CONFIG["warns_file"])

class Guardrails(commands.Cog):
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
            ch = guild.get_channel(LOG_CHANNEL_ID)
            if ch:
                await ch.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        if PROTECTED_ROLE_ID and any(role.id == PROTECTED_ROLE_ID for role in message.role_mentions):
            try:
                await message.delete()
            except Exception:
                pass

            warns = await WARNS_STORE.read()
            user_key = str(message.author.id)
            warns[user_key] = warns.get(user_key, 0) + 1
            await WARNS_STORE.write(warns)

            case_id = await self._next_case()
            reason = f"Attempted to ping protected role <@&{PROTECTED_ROLE_ID}>"
            dm = format_case_embed(discord, "Warning Issued", "Pinging this role is not allowed.", COLOR, message.guild.me, message.author, reason, case_id, FOOTER)
            try:
                await message.author.send(embed=dm)
            except Exception:
                pass

            pub = format_case_embed(discord, "Auto-Moderation: Protected Role Ping", f"Message by {message.author.mention} was removed.", COLOR, message.guild.me, message.author, reason, case_id, FOOTER)
            await self._log(message.guild, pub)

async def setup(bot: commands.Bot):
    await bot.add_cog(Guardrails(bot))
