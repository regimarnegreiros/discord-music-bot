import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import asyncio
import re

from config import COLOR

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn', 'executable': 'C:/ffmpeg/ffmpeg.exe'
}

YDL_OPTIONS = {
    'quiet': True,
    'ignoreerrors': True,
    'format': 'bestaudio',
    'noplaylist': True
}

YDL_OPTIONS_FLAT = {
    'extract_flat': 'in_playlist',
    'quiet': True,
    'ignoreerrors': True,
    'format': 'bestaudio',
    'noplaylist': True
}

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []
        super().__init__()

    @commands.command(aliases=['fila'])
    async def queue(self, ctx):
        if self.queue:
            if len(self.queue) > 20:
                queue_list = '\n'.join([f'{idx+1}. **{title}**' for idx, (_, title) in enumerate(self.queue[:20])])
                remaining_songs = len(self.queue) - 20
                await ctx.send(f'Fila de músicas (mostrando as primeiras 20):\n{queue_list}\n...e mais {remaining_songs} músicas na fila.')
            else:
                queue_list = '\n'.join([f'{idx+1}. **{title}**' for idx, (_, title) in enumerate(self.queue)])
                await ctx.send(f'Fila de músicas:\n{queue_list}')
        else:
            await ctx.send("A fila está vazia!")

    @commands.command(aliases=['clear'])
    async def clear_queue(self, ctx):
        self.queue.clear()
        await ctx.send("A fila foi limpa!")

    @commands.command(aliases=['entrar', 'connect'])
    async def join(self, ctx:commands.Context):
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect(timeout=30.0, reconnect=True)
            await ctx.send(f"Conectado ao canal de voz: {channel.name}")
        else:
            await ctx.send("Você precisa estar em um canal de voz para usar este comando.")

    @commands.command(aliases=['sair', 'disconnect'])
    async def exit(self, ctx:commands.Context):
        voice_client = ctx.guild.voice_client
        if voice_client:
            if voice_client.is_playing():
                voice_client.stop()
            await voice_client.disconnect()
            await ctx.send("Saindo do canal de voz.")
        else:
            await ctx.send("O bot não está atualmente em um canal de voz.")
        
    @commands.command(aliases=['pular'])
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("Pulando")

    def is_youtube_url(self, url):
        youtube_regex = re.compile(
            r'^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+$'
        )
        return youtube_regex.match(url) is not None
    
    def is_youtube_playlist_url(self, url):
        playlist_regex = re.compile(
            r'^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.*[?&]list=.+$'
        )
        return playlist_regex.match(url) is not None

    # Função assíncrona que extrai informações da playlist
    async def extract_playlist_info(self, url):
        loop = asyncio.get_running_loop()
        # Executa a função síncrona em um thread pool
        return await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(YDL_OPTIONS_FLAT).extract_info(url, download=False))

    @commands.command(aliases=['p'])
    async def play(self, ctx, *, search):
        voice_channel = ctx.author.voice.channel if ctx.author.voice else None
        if not voice_channel:
            return await ctx.send("Você precisa estar em um canal de voz para usar este comando.")
        if not ctx.voice_client:
            await voice_channel.connect()
            print(f"Conectado ao canal de voz: {voice_channel.name}")

        async with ctx.typing():
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                if self.is_youtube_playlist_url(search):
                    playlist_info = await self.extract_playlist_info(search)
                    await ctx.send(f'Adicionado a fila: **{playlist_info["title"]}** com {len(playlist_info["entries"])} músicas.')
                    
                    for entry in playlist_info['entries']:
                        if entry is None:
                            continue  # Ignora entradas que não puderam ser processadas

                        try:
                            song_info = await self.extract_playlist_info(entry['url'])
                            url = song_info['url']
                            title = song_info['title']
                            self.queue.append((url, title))
                            print(f'{COLOR["GREEN"]}Adicionada à fila: {COLOR["RESET"]}{title}')
                            
                            if ctx.voice_client and ctx.voice_client.is_connected() and not ctx.voice_client.is_playing():
                                await self.play_next(ctx)

                        except Exception as e:
                            print(f'{COLOR["RED"]}ERROR: {COLOR["RESET"]}{e}')
                            continue  # Continua com a próxima entrada na playlist

                elif self.is_youtube_url(search):
                    info = await asyncio.to_thread(ydl.extract_info, search, download=False)
                    url = info['url']
                    title = info['title']
                    self.queue.append((url, title))
                    await ctx.send(f'Adicionado a fila: **{title}**')
                    print(f'{COLOR["GREEN"]}Adicionada à fila: {COLOR["RESET"]}{title}')

                elif re.match(r'^https?:\/\/', search):
                    return await ctx.send("Isso não é um link do YouTube.")
                
                else:
                    info = await asyncio.to_thread(ydl.extract_info, f"ytsearch:{search}", download=False)
                    if 'entries' in info:
                        info = info['entries'][0]
                    url = info['url']
                    title = info['title']
                    self.queue.append((url, title))
                    await ctx.send(f'Adicionado a fila: **{title}**')
                    print(f'{COLOR["GREEN"]}Adicionada à fila: {COLOR["RESET"]}{title}')

        if not ctx.voice_client.is_playing():
            await self.play_next(ctx)

    async def play_next(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_connected():
            if self.queue:
                url, title = self.queue.pop(0)
                source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
                ctx.voice_client.play(source, after=lambda _: self.bot.loop.create_task(self.play_next(ctx)))
                await ctx.send(f'Tocando agora: **{title}**')
            else:
                await ctx.send("A fila está vazia!")

    ## Eventos
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        bot_voice_state = member.guild.voice_client

        if bot_voice_state and before.channel == bot_voice_state.channel and after.channel != bot_voice_state.channel:
            await asyncio.sleep(60)
            # Verificar o número de membros após o delay
            if len(bot_voice_state.channel.members) == 1:
                if bot_voice_state.is_playing():
                    bot_voice_state.stop()
                
                await bot_voice_state.disconnect()


async def setup(bot):
    await bot.add_cog(Music(bot))
