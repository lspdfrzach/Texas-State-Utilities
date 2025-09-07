import json
import asyncio
from typing import Any, Dict

class JSONStore:
    """Simple async-safe JSON read/write helper."""
    def __init__(self, path: str):
        self.path = path
        self._lock = asyncio.Lock()

    async def read(self) -> Dict[str, Any]:
        async with self._lock:
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except FileNotFoundError:
                return {}
    
    async def write(self, data: Dict[str, Any]) -> None:
        async with self._lock:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

def format_case_embed(discord, title: str, description: str, color: int, moderator, user=None, reason: str=None, case_id: int=None, footer_text: str=""):
    embed = discord.Embed(title=title, description=description, color=color)
    if user:
        embed.add_field(name="User", value=f"{user.mention} (`{user.id}`)", inline=False)
    if moderator:
        embed.add_field(name="Moderator", value=f"{moderator.mention} (`{moderator.id}`)", inline=False)
    if reason:
        embed.add_field(name="Reason", value=reason, inline=False)
    if case_id is not None:
        embed.add_field(name="Case ID", value=str(case_id), inline=True)
    if footer_text:
        embed.set_footer(text=footer_text)
    return embed

def has_any_role_id(member, role_id_list):
    role_ids = {r.id for r in member.roles}
    return any(rid in role_ids for rid in role_id_list)