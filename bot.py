import os
import json
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load env + config
load_dotenv()
with open("config.json","r",encoding="utf-8") as f:
    CONFIG = json.load(f)

PREFIX = CONFIG.get("prefix","!")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} ({bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"🔧 Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"Slash sync failed: {e}")

async def setup_cogs():
    for ext in ["cogs.moderation", "cogs.sessions", "cogs.guardrails"]:
        try:
            await bot.load_extension(ext)
            print(f"Loaded extension: {ext}")
        except Exception as e:
            print(f"Failed to load {ext}: {e}")

@bot.command()
@commands.is_owner()
async def sync(ctx):
    """Force sync slash commands."""
    await bot.tree.sync()
    await ctx.reply("Slash commands synced.")

bot.loop.create_task(setup_cogs())

token = os.getenv("DISCORD_TOKEN")
if not token:
    raise RuntimeError("DISCORD_TOKEN is missing. Put it in .env")

bot.run(token)