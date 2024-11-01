import discord
from discord.ext import commands
import yt_dlp
import asyncio
import deezer

from config.colors import COLOR
from config.ffmpeg import FFMPEG_OPTIONS
from config.ydl import *
from utils.send_embed import send_simple_embed
from utils.queue_manager import QueueManager

previous_now_playing_msgs = {}
send_queue_finish_msg = True

send_queue_finish_msg = True

def get_send_queue_finish_msg():
    return send_queue_finish_msg

def set_send_queue_finish_msg(value: bool):
    global send_queue_finish_msg
    send_queue_finish_msg = value

async def play_next(ctx: commands.Context, bot, queue_manager: QueueManager):
    guild_id = ctx.guild.id

    if not ctx.voice_client or not ctx.voice_client.is_connected():
        return

    try:
        queue = queue_manager.get_queue(guild_id)

        # Remove a mensagem de status anterior
        msg = previous_now_playing_msgs.pop(guild_id, None)
        if msg:
            await msg.delete()

        if not get_send_queue_finish_msg():
            set_send_queue_finish_msg(True)
            return
        
        if not queue:
            await send_simple_embed(
                ctx, "A fila de músicas terminou. Adicione mais músicas para continuar ouvindo!",
                discord.Color.blue()
            )
            return

        song_info = queue.pop(0)
        title = song_info.get('title', None)
        author = song_info.get('author', None)
        platform = song_info.get('platform', None)
        user_display_name = song_info.get('user_display_name', None)
        avatar_url = song_info.get('avatar_url', None)
        track_art_url = song_info.get('track_art_url', None)
        source_url = song_info.get('source_url', None)
        youtube_url = song_info.get('youtube_url', None)

        async with ctx.typing():
            try:
                ydl_opts = YDL_OPTIONS
                if platform == 'YouTube':
                    info = await asyncio.to_thread(yt_dlp.YoutubeDL(ydl_opts).extract_info, source_url, download=False)
                    author = info.get('artists', None)
                    if author:
                        author = ', '.join(author)
                    track_art_url = track_art_url or info.get('thumbnail')
                elif platform == 'Spotify':
                    info = await asyncio.to_thread(yt_dlp.YoutubeDL(ydl_opts).extract_info, f"ytsearch:{title} {author}", download=False)
                    if not info.get('entries'):
                        await send_simple_embed(ctx, "Nenhum resultado encontrado para a música do Spotify.", discord.Color.red())
                        return
                    info = info['entries'][0]
                elif platform == 'Deezer':
                    info = await asyncio.to_thread(yt_dlp.YoutubeDL(ydl_opts).extract_info, f"ytsearch:{title} {author}", download=False)
                    if not info.get('entries'):
                        await send_simple_embed(ctx, "Nenhum resultado encontrado para a música do Deezer.", discord.Color.red())
                        return
                    info = info['entries'][0]
                else:
                    await send_simple_embed(ctx, "Plataforma desconhecida para a música.", discord.Color.red())
                    return

                if not info or 'url' not in info:
                    await send_simple_embed(ctx, "Não foi possível obter a URL da música.", discord.Color.red())
                    return
            except Exception as e:
                print(f"Erro ao extrair informações: {e}")
                bot.loop.create_task(play_next(ctx, bot, queue_manager))
                return

        source = discord.FFmpegPCMAudio(info['url'], **FFMPEG_OPTIONS)
        ctx.voice_client.play(source, after=lambda _: bot.loop.create_task(play_next(ctx, bot, queue_manager)))

        color_map = {
            'YouTube': discord.Color.from_rgb(255, 0, 0),
            'Spotify': discord.Color.from_rgb(24, 216, 96),
            'Deezer': discord.Color.from_rgb(161, 56, 255)
        }
        icon_map = {
            'YouTube': 'youtube-icon.png',
            'Spotify': 'spotify-icon.png',
            'Deezer': 'deezer-icon.png'
        }

        embed = discord.Embed(
            title="Tocando agora",
            description=f'[{title}]({source_url})',
            color=color_map.get(platform, discord.Color.blue())
        )
        embed.set_author(name=platform, icon_url=f'attachment://{icon_map[platform]}', url=f'https://{platform.lower()}.com/')
        embed.set_thumbnail(url=track_art_url)
        if author is not None:
            embed.add_field(name="Artista", value=author)
        if info["duration"] > 420:
            embed.add_field(name="Duração", value=info["duration_string"], inline=True)
        embed.set_footer(text=f"Adicionado por {user_display_name}", icon_url=avatar_url)

        platform_icon_file = discord.File(f'icons/{icon_map[platform]}', icon_map[platform])
        previous_now_playing_msgs[guild_id] = await ctx.send(file=platform_icon_file, embed=embed, silent=True)
        print(f'{COLOR["BLUE"]}Tocando agora: {COLOR["RESET"]}{title}')

    except Exception as e:
        print(f"Erro na função play_next: {e}")
