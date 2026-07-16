from dataclasses import dataclass
from typing import Optional, Literal
import discord

@dataclass
class Song:
    title: str
    author: str
    source_url: str
    platform: Literal['YouTube', 'Spotify', 'Deezer']
    requester: discord.Member
    thumbnail: str
    stream_url: Optional[str] = None
