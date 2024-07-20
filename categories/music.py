import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import asyncio
import re

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn', 'executable': 'C:/ffmpeg/ffmpeg.exe'
}

YDL_OPTIONS = {
    'format' : 'bestaudio', 
    'noplaylist' : True
}

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []
        super().__init__()

    @commands.command(aliases=['fila'])
    async def queue(self, ctx):
        if self.queue:
            queue_list = '\n'.join([f'{idx+1}. **{title}**' for idx, (_, title) in enumerate(self.queue)])
            await ctx.send(f'Fila de músicas:\n{queue_list}')
        else:
            await ctx.send("A fila está vazia!")

    async def join_channel(self, ctx):
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect(timeout=30.0, reconnect=True)
            await ctx.send(f"Conectado ao canal de voz: {channel.name}")
            return True
        else:
            await ctx.send("Você precisa estar em um canal de voz para usar este comando.")
            return False

    @commands.command()
    async def join(self, ctx:commands.Context):
        await self.join_channel(ctx)

    async def exit_channel(self, ctx):
        voice_client = ctx.guild.voice_client
        if voice_client:
            await voice_client.disconnect()
            await ctx.send("Saindo do canal de voz.")
        else:
            await ctx.send("O bot não está atualmente em um canal de voz.")

    @commands.command()
    async def exit(self, ctx:commands.Context):
        await self.exit_channel(ctx)


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

    @commands.command(aliases=['p'])
    async def play(self, ctx, *, search):
        voice_channel = ctx.author.voice.channel if ctx.author.voice else None
        if not voice_channel:
            return await ctx.send("Você precisa estar em um canal de voz para usar este comando.")
        if not ctx.voice_client:
            await voice_channel.connect()

        async with ctx.typing():
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                if self.is_youtube_playlist_url(search):
                    return await ctx.send("Playlist do youtube ainda não suportada.")
                elif self.is_youtube_url(search):
                    info = ydl.extract_info(search, download=False)
                elif re.match(r'^https?:\/\/', search):
                    return await ctx.send("Isso não é um link do YouTube.")
                else:
                    info = ydl.extract_info(f"ytsearch:{search}", download=False)
                    if 'entries' in info:
                        info = info['entries'][0]
                url = info['url']
                title = info['title']
                self.queue.append((url, title))
                await ctx.send(f'Adicionado a fila: **{title}**')
        if not ctx.voice_client.is_playing():
            await self.play_next(ctx)

    async def play_next(self, ctx):
        if self.queue:
            url, title = self.queue.pop(0)
            source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
            ctx.voice_client.play(source, after=lambda _: self.bot.loop.create_task(self.play_next(ctx)))
            await ctx.send(f'Tocando agora: **{title}**')
        else:
            await ctx.send("A fila está vazia!")

    @commands.command()
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("Pulando")


async def setup(bot):
    await bot.add_cog(Music(bot))
