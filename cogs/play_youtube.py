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

    async def extract_info_yt(self, ctx, url):
        try:
            if is_youtube_playlist_url(url):
                ydl_opts = YDL_OPTIONS_FLAT
            elif is_youtube_url(url):
                ydl_opts = YDL_OPTIONS
            else:
                await send_simple_embed(ctx, "Formato não suportado!", discord.Color.red())
                return None, None

            info = await asyncio.to_thread(yt_dlp.YoutubeDL(ydl_opts).extract_info, url, download=False)
            is_playlist = 'entries' in info
            return info, is_playlist
        except Exception as e:
            await send_simple_embed(ctx, "Erro ao extrair informações!", discord.Color.red())
            print(e)
            return None, None

    async def add_song_to_queue(self, ctx, song_info):
        guild_id = ctx.guild.id
        queue_manager.add_to_queue(guild_id, song_info)

    async def process_entry(self, ctx, entry):
        if entry is None:
            return

        song_info = {
            'title': entry['title'],
            'author': entry.get('artists', None),
            'user_display_name': ctx.author.display_name,
            'avatar_url': ctx.author.avatar.url,
            'source_url': entry.get('webpage_url', entry['url']),
            'platform': 'YouTube',
            'youtube_url': entry['url'],
            'track_art_url': None
        }
        await self.add_song_to_queue(ctx, song_info)

    async def add_to_queue(self, ctx, info, is_playlist):
        if is_playlist:
            await send_simple_embed(
                ctx, f'Adicionando playlist: **{info["title"]}** com {len(info["entries"])} músicas.', 
                discord.Color.from_rgb(255, 0, 0)
            )
            for entry in info['entries']:
                await self.process_entry(ctx, entry)
        else:
            await self.process_entry(ctx, info)
            await send_simple_embed(ctx, f'Adicionado à fila: **{info["title"]}**', discord.Color.from_rgb(255, 0, 0))

    @commands.hybrid_command(aliases=['yt'], description="Adiciona uma música do youtube à fila. Suporta links do YouTube e pesquisas.")
    async def youtube(self, ctx: commands.Context, *, search):
        if not await connect_channel(ctx):
            return

        async with ctx.typing():
            if is_youtube_playlist_url(search) or is_youtube_url(search):
                info, is_playlist = await self.extract_info_yt(ctx, search)
            elif is_valid_url(search):
                await send_simple_embed(ctx, "Este link não é válido!", discord.Color.red())
                return
            else:
                info = await asyncio.to_thread(yt_dlp.YoutubeDL(YDL_OPTIONS_FLAT).extract_info, f"ytsearch:{search}", download=False)

                if info and info.get('entries', []):
                    if info['entries'][0].get('live_status') == 'is_live':
                        info = await asyncio.to_thread(yt_dlp.YoutubeDL(YDL_OPTIONS_FLAT).extract_info, f"ytsearch:{search} -live", download=False)
                    info = info['entries'][0] if 'entries' in info else info
                    is_playlist = False
                else:
                    await send_simple_embed(ctx, "Nenhum resultado encontrado. Tente novamente.", discord.Color.red())
                    return

            if info:
                await self.add_to_queue(ctx, info, is_playlist)

        if not ctx.voice_client.is_playing():
            try:
                await play_next(ctx, self.bot, queue_manager)
            except Exception as e:
                print(e)

async def setup(bot):
    await bot.add_cog(PlayYoutube(bot))
