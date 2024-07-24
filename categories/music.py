import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import asyncio
import re
import random

from config import COLOR

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -timeout 3000000 -nostdin',
    'options': '-vn', 'executable': 'C:/ffmpeg/ffmpeg.exe'
}

YDL_OPTIONS = {
    'quiet': True,
    'ignoreerrors': True,
    'format': 'bestaudio/best',
    'noplaylist': True
}

YDL_OPTIONS_FLAT = {
    'extract_flat': 'in_playlist',
    'quiet': True,
    'ignoreerrors': True,
    'format': 'bestaudio/best',
    'noplaylist': True
}

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []
        self.stop_adding_songs = False
        super().__init__()

    @commands.hybrid_command(aliases=['fila'], description="Mostra a fila de músicas.")
    async def queue(self, ctx):
        if self.queue:
            if len(self.queue) > 20:
                queue_list = '\n'.join([f'{idx+1}. {title}' for idx, (_, title) in enumerate(self.queue[:20])])
                remaining_songs = len(self.queue) - 20
                await ctx.send(f'```Fila de músicas:\n{queue_list}\n...e mais {remaining_songs} músicas na fila.```')
            else:
                queue_list = '\n'.join([f'{idx+1}. {title}' for idx, (_, title) in enumerate(self.queue)])
                await ctx.send(f'```Fila de músicas:\n{queue_list}```')
        else:
            embed = discord.Embed(
                description="A fila de músicas está vazia. Adicione algumas músicas para ver a lista!",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)

    @commands.hybrid_command(aliases=['clear', 'limpar'], description="Limpa a fila de músicas.")
    async def clear_queue(self, ctx:commands.Context):
        self.stop_adding_songs = True
        self.queue.clear()
        embed = discord.Embed(
            description="A fila foi limpa!",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(aliases=['entrar', 'connect'], description="Faz o bot entrar no canal de voz.")
    async def join(self, ctx:commands.Context):
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            if ctx.voice_client:
                if ctx.voice_client.channel == channel:
                    # O bot já está conectado ao canal de voz do usuário
                    if ctx.interaction:
                        embed = discord.Embed(
                            description="Já estou conectado a este canal de voz!",
                            color=discord.Color.green()
                        )
                        await ctx.send(embed=embed)
                    else:
                        await ctx.message.add_reaction('✅')
                else:
                    # O bot está conectado a outro canal, desconectar e conectar-se ao novo canal
                    await ctx.voice_client.move_to(channel)
                    if ctx.interaction:
                        embed = discord.Embed(
                            description="Conectado ao canal de voz!",
                            color=discord.Color.green()
                        )
                        message = await ctx.send(embed=embed)
                        await message.add_reaction('✅')
                    else:
                        await ctx.message.add_reaction('✅')
            else:
                # O bot não está conectado a nenhum canal
                await channel.connect(timeout=30.0, reconnect=True)
                if ctx.interaction:
                    embed = discord.Embed(
                        description="Conectado ao canal de voz!",
                        color=discord.Color.green()
                    )
                    message = await ctx.send(embed=embed)
                    await message.add_reaction('✅')
                else:
                    await ctx.message.add_reaction('✅')
                
                if not ctx.voice_client.is_playing():
                    await self.play_next(ctx) # Volta a tocar caso tenha músicas na fila

        else:
            embed = discord.Embed(
                description="Você precisa estar em um canal de voz para usar este comando!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.hybrid_command(aliases=['sair', 'disconnect'], description="Faz o bot sair do canal de voz.")
    async def exit(self, ctx:commands.Context):
        voice_client = ctx.guild.voice_client
        if voice_client:
            if voice_client.is_playing():
                voice_client.stop()
            await voice_client.disconnect()
            if ctx.interaction:
                embed = discord.Embed(
                    description="Saindo do canal de voz!",
                    color=discord.Color.green()
                )
                message = await ctx.send(embed=embed)
                await message.add_reaction('👋')
            else:
                await ctx.message.add_reaction('👋')
        else:
            embed = discord.Embed(
                description="O bot não está atualmente em um canal de voz!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        
    @commands.hybrid_command(aliases=['pular', 'next'], description="Pula para a próxima música na fila.")
    async def skip(self, ctx:commands.Context):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            if ctx.interaction:
                embed = discord.Embed(
                    description="Pulando música!",
                    color=discord.Color.blue()
                )
                message = await ctx.send(embed=embed)
                await message.add_reaction('⏭️')
            else:
                await ctx.message.add_reaction('⏭️')

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

    @commands.hybrid_command(aliases=['p'], description="Adiciona uma música à fila. Suporta links do YouTube e pesquisas.")
    async def play(self, ctx:commands.Context, *, search):
        voice_channel = ctx.author.voice.channel if ctx.author.voice else None
        if not voice_channel:
            embed = discord.Embed(
                description="Você precisa estar em um canal de voz para usar este comando!",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        if not ctx.voice_client:
            await voice_channel.connect()
            print(f"{COLOR["BOLD_WHITE"]}Conectado ao canal de voz: {COLOR["RESET"]}{voice_channel.name}")

        async with ctx.typing():
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                if self.is_youtube_playlist_url(search):
                    playlist_info = await self.extract_playlist_info(search)
                    embed = discord.Embed(
                        description=f'Adicionado a fila: **{playlist_info["title"]}** com {len(playlist_info["entries"])} músicas.',
                        color=discord.Color.blue()
                    )
                    await ctx.send(embed=embed)
                    
                    for entry in playlist_info['entries']:
                        if self.stop_adding_songs:
                            self.stop_adding_songs = False
                            self.queue.clear()
                            break  # Interrompe o loop se o comando clear for executado

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
                    embed = discord.Embed(
                        description=f'Adicionado a fila: **{title}**',
                        color=discord.Color.blue()
                    )
                    await ctx.send(embed=embed)
                    print(f'{COLOR["GREEN"]}Adicionada à fila: {COLOR["RESET"]}{title}')

                elif re.match(r'^https?:\/\/', search):
                    embed = discord.Embed(
                        description="Isso não é um link do YouTube!",
                        color= discord.Color.red()
                    )
                    return await ctx.send(embed=embed)
                
                else:
                    info = await asyncio.to_thread(ydl.extract_info, f"ytsearch:{search}", download=False)
                    if 'entries' in info:
                        info = info['entries'][0]
                    url = info['url']
                    title = info['title']
                    self.queue.append((url, title))
                    embed = discord.Embed(
                        description=f'Adicionado a fila: **{title}**',
                        color=discord.Color.blue()
                    )
                    await ctx.send(embed=embed)
                    print(f'{COLOR["GREEN"]}Adicionada à fila: {COLOR["RESET"]}{title}')

        if not ctx.voice_client.is_playing():
            await self.play_next(ctx)

    async def play_next(self, ctx:commands.Context):
        if ctx.voice_client and ctx.voice_client.is_connected():
            if self.queue:
                url, title = self.queue.pop(0)
                source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
                ctx.voice_client.play(source, after=lambda _: self.bot.loop.create_task(self.play_next(ctx)))
                embed = discord.Embed(
                    title="Tocando agora",
                    description=f'{title}',
                    color= discord.Color.blue()
                )
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    description="A fila de músicas terminou. Adicione mais músicas para continuar ouvindo!",
                    color=discord.Color.blue()
                )
                await ctx.send(embed=embed)

    @commands.hybrid_command(aliases=['remover'], description="Remove uma música da fila pelo índice.")
    async def remove(self, ctx: commands.Context, index: int):
        if index < 1 or index > len(self.queue):
            embed = discord.Embed(
                description="Índice inválido. Por favor, forneça um índice válido.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        else:
            removed_song = self.queue.pop(index - 1)
            embed = discord.Embed(
                description=f'Removido da fila: **{removed_song[1]}**',
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)

    @commands.hybrid_command(aliases=['embaralhar', 'aleatorizar'], description="Embaralha a fila de músicas.")
    async def random(self, ctx: commands.Context):
        if not self.queue:
            embed = discord.Embed(
                description="Não há músicas na fila para colocar no aleatório. Adicione algumas músicas primeiro!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        else:
            random.shuffle(self.queue)
            embed = discord.Embed(
                description="A fila de músicas foi embaralhada!",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)

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
