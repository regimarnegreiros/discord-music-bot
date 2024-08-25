import discord
from discord.ext import commands
from utils.connect_channel import connect_channel
import deezer
from utils.is_url import *
from utils.send_embed import send_simple_embed
from utils.queue_manager import queue_manager
from utils.play_next import play_next
from config.colors import COLOR

class PlayDeezer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = deezer.Client()
        super().__init__()

    @commands.hybrid_command(aliases=['dz'], description="Adiciona música/playlist/álbum do Deezer.")
    async def deezer(self, ctx: commands.Context, *, search):
        if not await connect_channel(ctx):
            return
        
        async with ctx.typing():
            try:
                tracks = []
                entity_name, album_art_url = None, None

                if "playlist" in search:
                    playlist_id = search.split("/")[-1]
                    playlist = self.client.get_playlist(playlist_id)
                    entity_name = playlist.title
                    tracks = playlist.tracks
                elif "album" in search:
                    album_id = search.split("/")[-1]
                    album = self.client.get_album(album_id)
                    entity_name = album.title
                    album_art_url = album.cover_xl
                    tracks = album.tracks
                elif "track" in search:
                    track_id = search.split("/")[-1]
                    track = self.client.get_track(track_id)
                    tracks = [track]
                elif is_valid_url(search):
                    await send_simple_embed(ctx, "Este link não é válido!", discord.Color.red())
                    return
                else:
                    search_results = self.client.search(search)
                    if not search_results:
                        await send_simple_embed(ctx, f'Nenhuma música encontrada para a pesquisa: **{search}**', discord.Color.red())
                        return

                    # Pegando apenas o primeiro resultado da pesquisa
                    track = search_results[0]
                    tracks = [track]

                if entity_name:
                    await send_simple_embed(ctx, f'Adicionando **{entity_name}** à fila.', discord.Color.from_rgb(161, 56, 255))

                for track in tracks:
                    artist = track.artist.name  # Acesso ao nome do artista principal
                    song_info = {
                        'title': track.title,
                        'author': artist,
                        'user_display_name': ctx.author.display_name,
                        'avatar_url': ctx.author.avatar.url,
                        'source_url': track.link,
                        'platform': 'Deezer',
                        'track_art_url': album_art_url or track.album.cover_xl
                    }
                    queue_manager.add_to_queue(ctx.guild.id, song_info)
                    print(f'{COLOR["GREEN"]}Adicionado à fila: {COLOR["RESET"]}{song_info["title"]}')

                    if not ("playlist" in search or "album" in search):
                        await send_simple_embed(
                            ctx, f'Adicionado à fila: **{song_info["title"]}** por **{song_info["author"]}**', 
                            discord.Color.from_rgb(161, 56, 255)
                        )

            except Exception as e:
                print("Erro ao buscar músicas do Deezer:", e)

        if not ctx.voice_client.is_playing():
            await play_next(ctx, self.bot, queue_manager)

async def setup(bot):
    await bot.add_cog(PlayDeezer(bot))
