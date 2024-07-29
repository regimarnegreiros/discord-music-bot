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

    async def send_embed(self, ctx, description, color):
        embed = discord.Embed(description=description, color=color)
        return await ctx.send(embed=embed)

    @commands.hybrid_command(aliases=['fila'], description="Mostra a fila de músicas.")
    async def queue(self, ctx: commands.Context):
        if self.queue:
            if len(self.queue) > 20:
                queue_list = '\n'.join([f'{idx+1}. {title}' for idx, (_, title, _, _, _) in enumerate(self.queue[:20])])
                remaining_songs = len(self.queue) - 20
                await ctx.send(f'```Fila de músicas:\n{queue_list}\n...e mais {remaining_songs} músicas na fila.```')
            else:
                queue_list = '\n'.join([f'{idx+1}. {title}' for idx, (_, title, _, _, _) in enumerate(self.queue)])
                await ctx.send(f'```Fila de músicas:\n{queue_list}```')
        else:
            await self.send_embed(
                ctx, "A fila de músicas está vazia. Adicione algumas músicas para ver a lista!",
                discord.Color.blue()
            )

    @commands.hybrid_command(aliases=['clear', 'limpar'], description="Limpa a fila de músicas.")
    async def clear_queue(self, ctx:commands.Context):
        self.stop_adding_songs = True
        self.queue.clear()
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
            
        if not ctx.voice_client.is_playing() and self.queue:
            await self.play_next(ctx) # Volta a tocar caso tenha músicas na fila

        if ctx.interaction:
            message = await self.send_embed(ctx, msg_text, discord.Color.green())
            await message.add_reaction('✅')
        else:
            await ctx.message.add_reaction('✅')

    @commands.hybrid_command(aliases=['sair', 'disconnect'], description="Faz o bot sair do canal de voz.")
    async def exit(self, ctx:commands.Context):
        voice_client = ctx.guild.voice_client
        if voice_client:
            if voice_client.is_playing():
                voice_client.stop()
            await voice_client.disconnect()
            if ctx.interaction:
                message = await self.send_embed(ctx, "Saindo do canal de voz!", discord.Color.green())
                await message.add_reaction('👋')
            else:
                await ctx.message.add_reaction('👋')
        else:
            await self.send_embed(ctx, "O bot não está atualmente em um canal de voz!", discord.Color.red())
        
    @commands.hybrid_command(aliases=['pular', 'next'], description="Pula para a próxima música na fila.")
    async def skip(self, ctx: commands.Context, amount: int = 0):
        if len(self.queue) == 0:
            # Se não há músicas na fila
            ctx.voice_client.stop()
            if ctx.interaction:
                await self.send_embed(ctx, "Não há músicas na fila para pular.", discord.Color.red())
            else:
                await ctx.message.add_reaction('⏭️')
            return
        
        if amount < 0 or amount > len(self.queue):
            await self.send_embed(ctx, "Por favor, insira um valor válido para pular músicas.", discord.Color.red())
            return

        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            # Pula a quantidade especificada de músicas
            self.queue = self.queue[amount:]
            if ctx.interaction:
                description = f"Pulando música!" if amount == 0 else f"Pulei {amount} músicas!"
                message = await self.send_embed(ctx, description, discord.Color.blue())
                await message.add_reaction('⏭️')
            else:
                await ctx.message.add_reaction('⏭️')

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

    # Função assíncrona que extrai informações da playlist
    async def extract_playlist_info(self, url):
        loop = asyncio.get_running_loop()
        # Executa a função síncrona em um thread pool
        return await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(YDL_OPTIONS_FLAT).extract_info(url, download=False))

    @commands.hybrid_command(aliases=['p'], description="Adiciona uma música à fila. Suporta links do YouTube e pesquisas.")
    async def play(self, ctx:commands.Context, *, search):
        voice_channel = ctx.author.voice.channel if ctx.author.voice else None
        if not voice_channel:
            await self.send_embed(ctx, "Você precisa estar em um canal de voz para usar este comando!", discord.Color.red())
            return
        if not ctx.voice_client:
            await voice_channel.connect()
            print(f"{COLOR["BOLD_WHITE"]}Conectado ao canal de voz: {COLOR["RESET"]}{voice_channel.name}")

        async with ctx.typing():
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                if self.is_youtube_playlist_url(search):
                    playlist_info = await self.extract_playlist_info(search)
                    await self.send_embed(
                        ctx, f'Adicionado a fila: **{playlist_info["title"]}** com {len(playlist_info["entries"])} músicas.', discord.Color.blue()
                    )
                    
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
                            webpage_url = song_info['webpage_url']
                            self.queue.append((url, title, webpage_url, ctx.author.display_name, ctx.author.avatar.url))
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
                    webpage_url = info['webpage_url']
                    self.queue.append((url, title, webpage_url, ctx.author.display_name, ctx.author.avatar.url))
                    await self.send_embed(ctx, f'Adicionado a fila: **{title}**', discord.Color.blue())
                    print(f'{COLOR["GREEN"]}Adicionada à fila: {COLOR["RESET"]}{title}')

                elif re.match(r'^https?:\/\/', search):
                    await self.send_embed(ctx, "Isso não é um link do YouTube!", discord.Color.red())
                    return
                
                else:
                    info = await asyncio.to_thread(ydl.extract_info, f"ytsearch:{search}", download=False)
                    if 'entries' in info:
                        info = info['entries'][0]
                    url = info['url']
                    title = info['title']
                    webpage_url = info['webpage_url']
                    self.queue.append((url, title, webpage_url, ctx.author.display_name, ctx.author.avatar.url))
                    await self.send_embed(ctx, f'Adicionado a fila: **{title}**', discord.Color.blue())
                    print(f'{COLOR["GREEN"]}Adicionada à fila: {COLOR["RESET"]}{title}')

        if not ctx.voice_client.is_playing():
            await self.play_next(ctx)

    async def play_next(self, ctx:commands.Context):
        if ctx.voice_client and ctx.voice_client.is_connected():
            if self.queue:
                url, title, webpage_url, display_name, avatar_url = self.queue.pop(0)
                source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
                ctx.voice_client.play(source, after=lambda _: self.bot.loop.create_task(self.play_next(ctx)))
                embed = discord.Embed(
                    title="Tocando agora",
                    description=f'[{title}]({webpage_url})',
                    color= discord.Color.blue()
                )
                embed.set_footer(text=f"Adicionado por {display_name}", icon_url=avatar_url)
                await ctx.send(embed=embed)
            else:
                await self.send_embed(
                    ctx, "A fila de músicas terminou. Adicione mais músicas para continuar ouvindo!",
                    discord.Color.blue()
                )

    @commands.hybrid_command(aliases=['remover'], description="Remove uma música da fila pelo índice.")
    async def remove(self, ctx: commands.Context, index: int):
        if index < 1 or index > len(self.queue):
            await self.send_embed(
                ctx, "Índice inválido. Por favor, forneça um índice válido.",
                discord.Color.red()
            )
        else:
            removed_song = self.queue.pop(index - 1)
            await self.send_embed(ctx, f'Removido da fila: **{removed_song[1]}**', discord.Color.blue)

    @commands.hybrid_command(aliases=['embaralhar', 'aleatorizar'], description="Embaralha a fila de músicas.")
    async def random(self, ctx: commands.Context):
        if not self.queue:
            await self.send_embed(
                ctx, "Não há músicas na fila para colocar no aleatório. Adicione algumas músicas primeiro!",
                discord.Color.red()
            )
        else:
            random.shuffle(self.queue)
            await self.send_embed(ctx, "A fila de músicas foi embaralhada!", discord.Color.blue())

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
