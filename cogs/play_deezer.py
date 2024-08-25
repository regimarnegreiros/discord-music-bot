import discord
from discord.ext import commands
from utils.connect_channel import connect_channel
import deezer
from utils.is_url import *
from utils.send_embed import send_simple_embed
from utils.queue_manager import queue_manager
from utils.play_next import play_next
from config.colors import COLOR
import requests  # Adicionado para resolver links curtos

class PlayDeezer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = deezer.Client()
        super().__init__()

    def resolve_deezer_link(self, short_link):
        # Resolve o link curto do Deezer para obter o ID real e o tipo de entidade (track, album, playlist).
        try:
            response = requests.head(short_link, allow_redirects=True)
            final_url = response.url
            if "playlist" in final_url:
                return "playlist", final_url.split("/")[-1]
            elif "album" in final_url:
                return "album", final_url.split("/")[-1]
            elif "track" in final_url:
                return "track", final_url.split("/")[-1]
            else:
                return None, None
        except Exception as e:
            print(f"Erro ao resolver link do Deezer: {e}")
            return None, None

    @commands.hybrid_command(aliases=['dz'], description="Adiciona música/playlist/álbum do Deezer.")
    async def deezer(self, ctx: commands.Context, *, search):
        if not await connect_channel(ctx):
            return
        
        async with ctx.typing():
            try:
                tracks = []
                entity_name, album_art_url = None, None

                # Verifica se o link é um link curto do Deezer
                if "deezer.page.link" in search:
                    entity_type, entity_id = self.resolve_deezer_link(search)
                    if not entity_type:
                        await send_simple_embed(ctx, "Este link não é válido!", discord.Color.red())
                        return
                else:
                    entity_type, entity_id = None, None

                if "playlist" in search or entity_type == "playlist":
                    playlist_id = entity_id or search.split("/")[-1]
                    playlist = self.client.get_playlist(playlist_id)
                    entity_name = playlist.title
                    tracks = playlist.tracks
                elif "album" in search or entity_type == "album":
                    album_id = entity_id or search.split("/")[-1]
                    album = self.client.get_album(album_id)
                    entity_name = album.title
                    album_art_url = album.cover_xl
                    tracks = album.tracks
                elif "track" in search or entity_type == "track":
                    track_id = entity_id or search.split("/")[-1]
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
                    song_info = {
                        'title': track.title,
                        'author': track.artist.name,
                        'user_display_name': ctx.author.display_name,
                        'avatar_url': ctx.author.avatar.url,
                        'source_url': track.link,
                        'platform': 'Deezer',
                        'track_art_url': album_art_url or track.album.cover_xl
                    }
                    
                    queue_manager.add_to_queue(ctx.guild.id, song_info)
                    print(f'{COLOR["GREEN"]}Adicionado à fila: {COLOR["RESET"]}{song_info["title"]}')

                    if not ("playlist" in search or "album" in search or entity_type == "playlist" or entity_type == "album"):
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
