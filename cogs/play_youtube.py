import discord
from discord.ext import commands
from utils.connect_channel import connect_channel
import asyncio
import yt_dlp
from utils.is_url import *
from config.ydl import *
from utils.send_embed import *
from config.colors import COLOR
from utils.queue_manager import queue_manager
from utils.play_next import play_next

class PlayYoutube(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @commands.hybrid_command(aliases=['yt'], description="Adiciona música/playlist do YouTube.")
    async def youtube(self, ctx: commands.Context, *, search):
        if not await connect_channel(ctx):
            return

        async with ctx.typing():
            if is_youtube_playlist_url(search) or is_youtube_url(search):
                info = await asyncio.to_thread(yt_dlp.YoutubeDL(YDL_OPTIONS_FLAT).extract_info, search, download=False)
                if 'entries' in info:
                    is_playlist = True
                    tracks = info['entries']
                else:
                    is_playlist = False
                    tracks = [info]

            elif is_valid_url(search):
                await send_simple_embed(ctx, "Este link não é válido!", discord.Color.red())
                return
            
            else:
                info = await asyncio.to_thread(yt_dlp.YoutubeDL(YDL_OPTIONS_FLAT).extract_info, f"ytsearch:{search}", download=False)

                if info and info.get('entries', []):
                    if info['entries'][0].get('live_status') == 'is_live':
                        info = await asyncio.to_thread(yt_dlp.YoutubeDL(YDL_OPTIONS_FLAT).extract_info, f"ytsearch:{search} -live", download=False)
                    tracks = info['entries'] if isinstance(info['entries'], list) else [info]
                    is_playlist = False
                else:
                    await send_simple_embed(ctx, "Nenhum resultado encontrado. Tente novamente.", discord.Color.red())
                    return

            if is_playlist:
                await send_simple_embed(
                    ctx, f'Adicionando playlist: **{info["title"]}** à fila.', 
                    discord.Color.from_rgb(255, 0, 0)
                )
            try:
                for track in tracks:
                    song_info = {
                        'title': track.get('title', None),
                        'author': track.get('artists', None),
                        'user_display_name': ctx.author.display_name,
                        'avatar_url': ctx.author.avatar.url,
                        'source_url': track.get('webpage_url', track['url']),
                        'platform': 'YouTube',
                        'youtube_url': track.get('url', None),
                        'track_art_url': track.get('thumbnail', None)
                    }
                    queue_manager.add_to_queue(ctx.guild.id, song_info)
                    print(f'{COLOR["GREEN"]}Adicionado à fila: {COLOR["RESET"]}{song_info["title"]}')
                
                if not is_playlist:
                    await send_simple_embed(ctx, f'Adicionado à fila: **{song_info["title"]}**', discord.Color.from_rgb(255, 0, 0))
            except Exception as e:
                print(f"Erro ao adicionar música à fila: {e}")

        if not ctx.voice_client.is_playing():
            await play_next(ctx, self.bot, queue_manager)

async def setup(bot):
    await bot.add_cog(PlayYoutube(bot))
