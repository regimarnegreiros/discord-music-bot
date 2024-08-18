import discord
from discord.ext import commands

from config.colors import COLOR
from utils.send_embed import send_simple_embed

async def connect_channel(ctx: commands.Context):
    voice_channel = ctx.author.voice.channel if ctx.author.voice else None
    if not voice_channel:
        await send_simple_embed(ctx, "Você precisa estar em um canal de voz para usar este comando!", discord.Color.red())
        return False
    if not ctx.voice_client:
        await voice_channel.connect()
        print(f"{COLOR['BOLD_WHITE']}Conectado ao canal de voz: {COLOR['RESET']}{voice_channel.name}")
    return True