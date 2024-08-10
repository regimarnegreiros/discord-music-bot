import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import asyncio
import re
import random
import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from config import COLOR, FFMPEG_OPTIONS, YDL_OPTIONS, YDL_OPTIONS_FLAT

load_dotenv()
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}
        self.previous_now_playing_msg = None
        super().__init__()

        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
                client_id=SPOTIPY_CLIENT_ID,
                client_secret=SPOTIPY_CLIENT_SECRET
        ))

    @commands.hybrid_command(aliases=['sp'], description="Adiciona uma música ou playlist do Spotify à fila.")
    async def spotify(self, ctx: commands.Context, *, search):
        if not await self.connect_to_play(ctx):
            return

        async with ctx.typing():
            try:
                tracks = []
                entity_name = ""

                if "playlist" in search:
                    results = self.sp.playlist_tracks(search)
                    entity_name = self.sp.playlist(search)['name']
                    tracks = results['items']
                    await self.send_embed(ctx, f'Adicionando playlist: **{entity_name}** à fila.', discord.Color.from_rgb(24, 216, 96))
                elif "album" in search:
                    results = self.sp.album_tracks(search)
                    entity_name = self.sp.album(search)['name']
                    tracks = results['items']
                    await self.send_embed(ctx, f'Adicionando álbum: **{entity_name}** à fila.', discord.Color.from_rgb(24, 216, 96))
                elif "track" in search:
                    results = self.sp.track(search)
                    entity_name = results['name']
                    tracks = [results]
                elif re.match(r'^https?:\/\/', search):
                    await self.send_embed(ctx, "Este link não é válido!", discord.Color.red())
                    return
                else:
                    results = self.sp.search(q=search, type='track', limit=1)
                    tracks = results['tracks']['items']

                    if not tracks:
                        await self.send_embed(ctx, f'Nenhuma música encontrada para a pesquisa: **{search}**', discord.Color.red())
                        return

                for track in tracks:
                    track_name = track['name'] if 'name' in track else track['track']['name']
                    track_artists = ', '.join([artist['name'] for artist in track['artists']]) if 'artists' in track else ', '.join([artist['name'] for artist in track['track']['artists']])
                    track_url = track['external_urls']['spotify'] if 'external_urls' in track else track['track']['external_urls']['spotify']
                   
                    # Extrair a URL da capa da música
                    track_art_url = track['album']['images'][0]['url'] if 'album' in track else track['track']['album']['images'][0]['url']

                    song_info = {
                        'title': track_name,
                        'author': track_artists,
                        'user_display_name': ctx.author.display_name,
                        'avatar_url': ctx.author.avatar.url,
                        'source_url': track_url,
                        'platform': 'Spotify',
                        'youtube_url': None,  # Será preenchido na hora de tocar
                        'track_art_url': track_art_url
                    }
                    self.get_queue(ctx.guild.id).append(song_info)
                    if not "playlist" in search and not "album" in search:
                        await self.send_embed(ctx, f'Adicionado à fila: **{track_name}** por **{track_artists}**', discord.Color.from_rgb(24, 216, 96))
                    print(f'{COLOR["GREEN"]}Adicionado à fila: {COLOR["RESET"]}{song_info["title"]}')

            except Exception as e:
                await self.send_embed(ctx, f'Erro ao buscar músicas do Spotify: {str(e)}', discord.Color.red())

        if not ctx.voice_client.is_playing():
            await self.play_next(ctx)

    async def send_embed(self, ctx, description, color):
        embed = discord.Embed(description=description, color=color)
        return await ctx.send(embed=embed)

    def get_queue(self, guild_id):
        if guild_id not in self.queues:
            self.queues[guild_id] = []
        return self.queues[guild_id]

    @commands.hybrid_command(aliases=['fila'], description="Mostra a fila de músicas.")
    async def queue(self, ctx: commands.Context):
        queue = self.get_queue(ctx.guild.id)
        if not queue:
            await self.send_embed(
                ctx, "A fila de músicas está vazia. Adicione algumas músicas para ver a lista!",
                discord.Color.blue()
            )
            return
        
        queue_list = '\n'.join([f'{idx+1}. {song_info["title"]}' for idx, song_info in enumerate(queue[:20])])
        remaining_songs = len(queue) - 20
        message_content = f'```{queue_list}```'
        if remaining_songs > 0:
            message_content += f'```\n...e mais {remaining_songs} músicas na fila.```'
        await ctx.send(message_content)

    @commands.hybrid_command(aliases=['clear', 'limpar'], description="Limpa a fila de músicas.")
    async def clear_queue(self, ctx: commands.Context):
        self.get_queue(ctx.guild.id).clear()
        await self.send_embed(ctx, "A fila foi limpa!", discord.Color.blue())

    @commands.hybrid_command(aliases=['entrar', 'connect'], description="Faz o bot entrar no canal de voz.")
    async def join(self, ctx: commands.Context):
        if not ctx.author.voice:
            await self.send_embed(ctx, "Você precisa estar em um canal de voz para usar este comando!", discord.Color.red())
            return

        channel = ctx.author.voice.channel
        message = None
        
        if ctx.voice_client:
            if ctx.voice_client.channel == channel:
                msg_text = "Já estou conectado a este canal de voz!"
            else:
                await ctx.voice_client.move_to(channel)
                msg_text = "Conectado ao canal de voz!"
        else:
            await channel.connect(timeout=30.0, reconnect=True)
            msg_text = "Conectado ao canal de voz!"
            
        if not ctx.voice_client.is_playing() and self.get_queue(ctx.guild.id):
            await self.play_next(ctx) # Volta a tocar caso tenha músicas na fila

        if ctx.interaction:
            message = await self.send_embed(ctx, msg_text, discord.Color.green())
            await message.add_reaction('✅')
        else:
            await ctx.message.add_reaction('✅')

    @commands.hybrid_command(aliases=['sair', 'disconnect'], description="Faz o bot sair do canal de voz.")
    async def exit(self, ctx: commands.Context):
        voice_client = ctx.guild.voice_client

        if not voice_client:
            await self.send_embed(ctx, "O bot não está atualmente em um canal de voz!", discord.Color.red())
            return

        if voice_client.is_playing():
            voice_client.stop()
        
        await voice_client.disconnect()

        if ctx.interaction:
            message = await self.send_embed(ctx, "Saindo do canal de voz!", discord.Color.green())
            await message.add_reaction('👋')
        else:
            await ctx.message.add_reaction('👋')
        
    @commands.hybrid_command(aliases=['pular', 'next'], description="Pula para a próxima música na fila.")
    async def skip(self, ctx: commands.Context, amount: int = 0):
        queue = self.get_queue(ctx.guild.id)
        if amount < 0 or amount > len(queue):
            await self.send_embed(ctx, "Por favor, insira um valor válido para pular músicas.", discord.Color.red())
            return

        if ctx.voice_client and ctx.voice_client.is_playing():
            if queue:
                # Se há músicas na fila, pula a quantidade especificada de músicas
                self.queues[ctx.guild.id] = self.queues[ctx.guild.id][amount:]
                ctx.voice_client.stop()
                if ctx.interaction:
                    description = f"Pulando música!" if amount == 0 else f"Pulei {amount} músicas!"
                    message = await self.send_embed(ctx, description, discord.Color.blue())
                    await message.add_reaction('⏭️')
                else:
                    await ctx.message.add_reaction('⏭️')
            else:
                # Se a fila está vazia, apenas para a reprodução atual
                ctx.voice_client.stop()
                if ctx.interaction:
                    await self.send_embed(ctx, "Não há músicas na fila para pular.", discord.Color.red())
                else:
                    await ctx.message.add_reaction('⏭️')

    async def connect_to_play(self, ctx: commands.Context):
        voice_channel = ctx.author.voice.channel if ctx.author.voice else None
        if not voice_channel:
            await self.send_embed(ctx, "Você precisa estar em um canal de voz para usar este comando!", discord.Color.red())
            return False
        if not ctx.voice_client:
            await voice_channel.connect()
            print(f"{COLOR['BOLD_WHITE']}Conectado ao canal de voz: {COLOR['RESET']}{voice_channel.name}")
        return True

    def is_spotify_url(self, url):
        spotify_regex = re.compile(
            r'^https?:\/\/(open\.spotify\.com)\/.*'
        )
        return spotify_regex.match(url) is not None

    def is_youtube_url(self, url):
        youtube_regex = re.compile(
            r'^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.*[?&]v=.*$'
        )
        return youtube_regex.match(url) is not None
    
    def is_youtube_playlist_url(self, url):
        playlist_regex = re.compile(
            r'^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.*[?&]list=.+$'
        )
        return playlist_regex.match(url) is not None and 'v=' not in url

    # Função assíncrona que extrai informações das músicas
    async def extract_info_yt(self, url):
        loop = asyncio.get_running_loop()
        if self.is_youtube_playlist_url(url):
            info = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(YDL_OPTIONS_FLAT).extract_info(url, download=False))
        if self.is_youtube_url(url):
            info = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(YDL_OPTIONS).extract_info(url, download=False))

        if 'entries' in info:
            return info, True  # É uma playlist
        else:
            return info, False  # É um vídeo individual

    async def add_to_queue(self, ctx, info, is_playlist):
        guild_id = ctx.guild.id

        if is_playlist:
            await self.send_embed(
                ctx, f'Adicionando playlist: **{info["title"]}** com {len(info["entries"])} músicas.', discord.Color.from_rgb(255, 0, 0)
            )

            for entry in info['entries']:
                if entry is None:
                    continue

                song_info = {
                    'title': entry['title'],
                    'author': None,
                    'user_display_name': ctx.author.display_name,
                    'avatar_url': ctx.author.avatar.url,
                    'source_url': entry['url'],  # O URL da fonte original (YouTube)
                    'platform': 'YouTube',  # Especifica que a fonte é o YouTube
                    'youtube_url': entry['url'],  # Já define o URL do YouTube, pois é uma música do YouTube
                    'track_art_url': None # Será preenchido na hora de tocar
                }
                self.get_queue(guild_id).append(song_info)
                print(f'{COLOR["GREEN"]}Adicionado à fila: {COLOR["RESET"]}{song_info["title"]}')
        else:
            song_info = {
                'title': info['title'],
                'author': None,
                'user_display_name': ctx.author.display_name,
                'avatar_url': ctx.author.avatar.url,
                'source_url': info.get('webpage_url', info['url']),  # O URL da fonte original (YouTube)
                'platform': 'YouTube',  # Especifica que a fonte é o YouTube
                'youtube_url': info['url'],  # Já define o URL do YouTube, pois é uma música do YouTube
                'track_art_url': None # Será preenchido na hora de tocar
            }
            self.get_queue(guild_id).append(song_info)
            await self.send_embed(ctx, f'Adicionado à fila: **{song_info["title"]}**', discord.Color.from_rgb(255, 0, 0))
            print(f'{COLOR["GREEN"]}Adicionado à fila: {COLOR["RESET"]}{song_info["title"]}')

    @commands.hybrid_command(aliases=['p'], description="Adiciona uma música à fila. Suporta links do YouTube e pesquisas.")
    async def play(self, ctx: commands.Context, *, search):
        if not await self.connect_to_play(ctx):
            return

        async with ctx.typing():
            if self.is_youtube_playlist_url(search) or self.is_youtube_url(search):
                try:
                    info, is_playlist = await self.extract_info_yt(search)
                    await self.add_to_queue(ctx, info, is_playlist)
                except Exception as e:
                    print(f'Error: {e}')

            elif self.is_spotify_url(search):
                await self.spotify(ctx, search=search)
                return

            elif re.match(r'^https?:\/\/', search):
                await self.send_embed(ctx, "Este link não é válido!", discord.Color.red())
                return

            else:
                info = await asyncio.to_thread(yt_dlp.YoutubeDL(YDL_OPTIONS_FLAT).extract_info, f"ytsearch:{search}", download=False)
                if 'entries' in info and len(info['entries']) > 0:
                    if info['entries'][0]['live_status'] == 'is_live':
                        info = await asyncio.to_thread(yt_dlp.YoutubeDL(YDL_OPTIONS_FLAT).extract_info, f"ytsearch:{search} -live", download=False)

                if 'entries' in info and len(info['entries']) > 0:
                    info = info['entries'][0]
                    await self.add_to_queue(ctx, info, False)
                else:
                    await self.send_embed(ctx, "Nenhum resultado encontrado. Tente novamente.", discord.Color.red())
                    return

        if not ctx.voice_client.is_playing():
            await self.play_next(ctx)

    async def play_next(self, ctx: commands.Context):
        guild_id = ctx.guild.id
        if ctx.voice_client and ctx.voice_client.is_connected():
            queue = self.get_queue(guild_id)

            if self.previous_now_playing_msg is not None:
                try:
                    await self.previous_now_playing_msg.delete()
                except Exception as e:
                    print(f"Erro ao deletar mensagem: {e}")

            if queue:
                song_info = queue.pop(0)
                title = song_info.get('title')
                author = song_info.get('author')
                user_display_name = song_info.get('user_display_name')
                avatar_url = song_info.get('avatar_url')
                source_url = song_info.get('source_url')
                platform = song_info.get('platform')
                track_art_url = song_info.get('track_art_url')

                async with ctx.typing():
                    if platform == 'YouTube':
                        # Extrair informações diretamente do YouTube
                        info = await asyncio.to_thread(yt_dlp.YoutubeDL(YDL_OPTIONS).extract_info, source_url, download=False)
                        track_art_url = info.get('thumbnail')
                    elif platform == 'Spotify':
                        # Realizar pesquisa no YouTube para encontrar a música do Spotify
                        info = await asyncio.to_thread(yt_dlp.YoutubeDL(YDL_OPTIONS).extract_info, f"ytsearch:{title} {author}", download=False)
                        
                        if 'entries' in info and len(info['entries']) > 0:
                            # Pega o primeiro resultado da pesquisa
                            info = info['entries'][0]
                        else:
                            await self.send_embed(ctx, "Nenhum resultado encontrado para a música do Spotify.", discord.Color.red())
                            return
                    else:
                        await self.send_embed(ctx, "Plataforma desconhecida para a música.", discord.Color.red())
                        return

                    if not info:
                        return

                source = discord.FFmpegPCMAudio(info['url'], **FFMPEG_OPTIONS)
                ctx.voice_client.play(source, after=lambda _: self.bot.loop.create_task(self.play_next(ctx)))

                if platform == 'YouTube':
                    embed = discord.Embed(
                        title="Tocando agora",
                        description=f'[{title}]({source_url})',
                        color=discord.Color.from_rgb(255, 0, 0)
                    )
                    platform_icon_file = discord.File('icons/youtube-icon.png', 'youtube-icon.png')
                    embed.set_author(name=platform,icon_url='attachment://youtube-icon.png', url='https://www.youtube.com/')
                    embed.set_thumbnail(url=track_art_url)
                    embed.set_footer(text=f"Adicionado por {user_display_name}", icon_url=avatar_url)
                
                elif platform == 'Spotify':
                    embed = discord.Embed(
                        title="Tocando agora",
                        description=f'[{title}]({source_url})',
                        color=discord.Color.from_rgb(24, 216, 96)
                    )
                    platform_icon_file = discord.File('icons/spotify-icon.png', 'spotify-icon.png')
                    embed.set_author(name=platform, icon_url='attachment://spotify-icon.png', url='https://open.spotify.com/')
                    embed.set_thumbnail(url=track_art_url)
                    embed.add_field(name="Artista", value=author)
                    embed.set_footer(text=f"Adicionado por {user_display_name}", icon_url=avatar_url)
    
                self.previous_now_playing_msg = await ctx.send(file=platform_icon_file, embed=embed)
            else:
                self.previous_now_playing_msg = None
                await self.send_embed(
                    ctx, "A fila de músicas terminou. Adicione mais músicas para continuar ouvindo!",
                    discord.Color.blue()
                )

    @commands.hybrid_command(aliases=['remover'], description="Remove uma música da fila pelo índice.")
    async def remove(self, ctx: commands.Context, index: int):
        queue = self.get_queue(ctx.guild.id)
        if index < 1 or index > len(queue):
            await self.send_embed(
                ctx, "Índice inválido. Por favor, forneça um índice válido.",
                discord.Color.red()
            )
        else:
            removed_song = queue.pop(index - 1)
            await self.send_embed(ctx, f'Removido da fila: **{removed_song[1]}**', discord.Color.blue())

    @commands.hybrid_command(aliases=['embaralhar', 'aleatorizar'], description="Embaralha a fila de músicas.")
    async def random(self, ctx: commands.Context):
        queue = self.get_queue(ctx.guild.id)
        if not queue:
            await self.send_embed(
                ctx, "Não há músicas na fila para colocar no aleatório. Adicione algumas músicas primeiro!",
                discord.Color.red()
            )
        else:
            random.shuffle(queue)
            await self.send_embed(ctx, "A fila de músicas foi embaralhada!", discord.Color.blue())

    @commands.hybrid_command(aliases=['mover'], description="Move uma música na fila de uma posição para outra.")
    async def move(self, ctx: commands.Context, from_index: int, to_index: int):
        queue = self.get_queue(ctx.guild.id)
        if from_index < 1 or from_index > len(queue) or to_index < 1 or to_index > len(queue):
            await self.send_embed(
                ctx, "Índice inválido. Por favor, forneça índices válidos.",
                discord.Color.red()
            )
        else:
            song = queue.pop(from_index - 1)
            queue.insert(to_index - 1, song)
            await self.send_embed(
                ctx, f'Movido **{song[1]}** da posição {from_index} para a posição {to_index}.',
                discord.Color.blue()
            )

    ## Eventos
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        bot_voice_state = member.guild.voice_client

        if bot_voice_state and before.channel == bot_voice_state.channel and after.channel != bot_voice_state.channel:
            for _ in range(300):
                await asyncio.sleep(1)
                if len(bot_voice_state.channel.members) > 1:
                    return
            
            if len(bot_voice_state.channel.members) == 1:
                if bot_voice_state.is_playing():
                    bot_voice_state.stop()
                
                await bot_voice_state.disconnect()
                self.get_queue(member.guild.id).clear()

async def setup(bot):
    await bot.add_cog(Music(bot))
