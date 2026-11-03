import discord
from discord.ext import commands
from utils.connect_channel import connect_channel
import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from utils.is_url import *
from utils.send_embed import send_simple_embed
from utils.queue_manager import queue_manager
from utils.play_next import play_next
from config.colors import COLOR

load_dotenv()
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')

class PlaySpotify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=SPOTIPY_CLIENT_ID,
                client_secret=SPOTIPY_CLIENT_SECRET
            )
        )
        super().__init__()

    @commands.hybrid_command(aliases=['sp'], description="Adiciona música/playlist/álbum do Spotify.")
    async def spotify(self, ctx: commands.Context, *, search):
        if not await connect_channel(ctx):
            return
        
        async with ctx.typing():
            try:
                tracks = []
                entity_name, album_art_url = None, None

                if "playlist" in search:
                    playlist = self.sp.playlist(search)
                    entity_name, tracks = playlist['name'], playlist['tracks']['items']
                elif "album" in search:
                    album = self.sp.album(search)
                    entity_name, album_art_url = album['name'], album['images'][0]['url']
                    tracks = album['tracks']['items']
                elif "track" in search:
                    track = self.sp.track(search)
                    entity_name, tracks = None, [track]
                elif is_valid_url(search):
                    await send_simple_embed(ctx, "Este link não é válido!", discord.Color.red())
                    return
                else:
                    search_results = self.sp.search(q=search, type='track', limit=1)
                    tracks = search_results['tracks']['items']
                    if not tracks:
                        await send_simple_embed(ctx, f'Nenhuma música encontrada para a pesquisa: **{search}**', discord.Color.red())
                        return

                if entity_name:
                    await send_simple_embed(ctx, f'Adicionando **{entity_name}** à fila.', discord.Color.from_rgb(24, 216, 96))

                for track in tracks:
                    track_info = track.get('track', track)
                    song_info = {
                        'title': track_info['name'],
                        'author': ', '.join(artist['name'] for artist in track_info['artists']),
                        'user_display_name': ctx.author.display_name,
                        'avatar_url': ctx.author.avatar.url,
                        'source_url': track_info['external_urls']['spotify'],
                        'platform': 'Spotify',
                        'track_art_url': album_art_url or track_info['album']['images'][0]['url']
                    }
                    queue_manager.add_to_queue(ctx.guild.id, song_info)
                    print(f'{COLOR["GREEN"]}Adicionado à fila: {COLOR["RESET"]}{song_info["title"]}')

                    if not ("playlist" in search or "album" in search):
                        await send_simple_embed(ctx, f'Adicionado à fila: **{song_info["title"]}** por **{song_info["author"]}**', discord.Color.from_rgb(24, 216, 96))

            except Exception as e:
                print("Erro ao buscar músicas do Spotify:", e)

        if not ctx.voice_client.is_playing():
            await play_next(ctx, self.bot, queue_manager)

async def setup(bot):
    await bot.add_cog(PlaySpotify(bot))
