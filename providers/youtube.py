import re
import asyncio
import discord
import yt_dlp
from models.song import Song
from providers.base import BaseProvider
from config.ydl import YDL_OPTIONS, YDL_OPTIONS_FLAT

class YouTubeProvider(BaseProvider):
    """Provedor responsável pela extração de metadados do YouTube."""

    # Padrões de URL para vídeos e playlists do YouTube
    YOUTUBE_REGEX = re.compile(r'^(https?://)?(www\.|music\.)?(youtube\.com|youtu\.be)/.+')
    PLAYLIST_REGEX = re.compile(r'^(https?://)?(www\.|music\.)?youtube\.com/(playlist\?|.*[?&]list=)[A-Za-z0-9_-]+')

    @property
    def name(self) -> str:
        return 'YouTube'

    @property
    def color(self) -> discord.Color:
        return discord.Color.from_rgb(255, 0, 0)

    @property
    def icon_file(self) -> str:
        return 'youtube-icon.png'

    @classmethod
    def matches(cls, url: str) -> bool:
        """Verifica se a URL pertence ao domínio do YouTube sem precisar instanciar a classe."""
        return cls.YOUTUBE_REGEX.match(url) is not None

    def _entry_to_song(self, entry: dict, requester: discord.Member) -> Song:
        """Converte o dicionário bruto retornado pelo yt-dlp em uma instância padronizada de Song."""
        # Obtém o autor (pode vir como 'uploader' ou lista 'artists' no yt-dlp)
        author = entry.get('uploader') or entry.get('artists')
        if isinstance(author, list):
            author = ', '.join(author)

        # Garante que a URL seja absoluta caso venha apenas o ID do vídeo
        source_url = entry.get('webpage_url') or entry.get('url')
        if source_url and not source_url.startswith('http'):
            source_url = f"https://www.youtube.com/watch?v={source_url}"

        return Song(
            title=entry.get('title', 'Sem título'),
            author=author or 'Desconhecido',
            source_url=source_url or '',
            platform='YouTube',
            requester=requester,
            thumbnail=entry.get('thumbnail', '')
        )

    async def search(self, query: str, requester: discord.Member) -> list[Song]:
        """Busca textual rápida via 'ytsearch:', ignorando transmissões ao vivo."""
        info = await asyncio.to_thread(
            yt_dlp.YoutubeDL(YDL_OPTIONS_FLAT).extract_info,
            f"ytsearch:{query}",
            download=False
        )

        if not info or not info.get('entries'):
            return []

        first = info['entries'][0]

        # Se o primeiro resultado for uma live stream, refaz a busca excluindo lives
        if first.get('live_status') == 'is_live':
            info = await asyncio.to_thread(
                yt_dlp.YoutubeDL(YDL_OPTIONS_FLAT).extract_info,
                f"ytsearch:{query} -live",
                download=False
            )
            if not info or not info.get('entries'):
                return []
            first = info['entries'][0]

        return [self._entry_to_song(first, requester)]

    async def get_track(self, url_or_id: str, requester: discord.Member) -> Song | None:
        """Obtém os metadados de um único vídeo do YouTube."""
        info = await asyncio.to_thread(
            yt_dlp.YoutubeDL(YDL_OPTIONS).extract_info,
            url_or_id,
            download=False
        )

        if not info:
            return None

        return self._entry_to_song(info, requester)

    async def get_playlist(self, url_or_id: str, requester: discord.Member) -> list[Song]:
        """Extrai apenas os metadados em lote de uma playlist (modo flat, sem baixar áudio antecipado)."""
        info = await asyncio.to_thread(
            yt_dlp.YoutubeDL(YDL_OPTIONS_FLAT).extract_info,
            url_or_id,
            download=False
        )

        if not info or not info.get('entries'):
            return []

        return [self._entry_to_song(entry, requester) for entry in info['entries'] if entry]

    async def extract(self, query: str, requester: discord.Member) -> list[Song]:
        """Roteia a entrada automaticamente para playlist, vídeo individual ou busca textual."""
        # Se for link de playlist sem parâmetro de vídeo único ('v=')
        if self.PLAYLIST_REGEX.match(query) and 'v=' not in query:
            return await self.get_playlist(query, requester)

        # Se for link direto de vídeo
        elif self.matches(query):
            track = await self.get_track(query, requester)
            return [track] if track else []

        # Caso contrário, trata como busca por nome
        return await self.search(query, requester)
