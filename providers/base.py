from abc import ABC, abstractmethod
import discord
from models.song import Song

class BaseProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Nome identificador da plataforma (ex: 'YouTube', 'Spotify', 'Deezer')."""
        pass

    @property
    @abstractmethod
    def color(self) -> discord.Color:
        """Cor característica da plataforma para embeds e mensagens."""
        pass

    @property
    @abstractmethod
    def icon_file(self) -> str:
        """Nome do arquivo de ícone da plataforma na pasta icons/ (ex: 'youtube-icon.png')."""
        pass

    @classmethod
    @abstractmethod
    def matches(cls, url: str) -> bool:
        """Verifica se a URL informada pertence a esta plataforma."""
        pass

    @abstractmethod
    async def search(self, query: str, requester: discord.Member) -> list[Song]:
        """Realiza busca textual por nome de música/artista."""
        pass

    @abstractmethod
    async def get_track(self, url_or_id: str, requester: discord.Member) -> Song | None:
        """Obtém metadados de uma única faixa por URL ou ID."""
        pass

    @abstractmethod
    async def get_playlist(self, url_or_id: str, requester: discord.Member) -> list[Song]:
        """Obtém todas as músicas de uma playlist por URL ou ID."""
        pass

    async def get_album(self, url_or_id: str, requester: discord.Member) -> list[Song]:
        """Obtém todas as músicas de um álbum (por padrão pode delegar para get_playlist)."""
        return await self.get_playlist(url_or_id, requester)

    @abstractmethod
    async def extract(self, query: str, requester: discord.Member) -> list[Song]:
        """Método unificado: detecta se a query é link (track/album/playlist) ou busca textual e devolve as faixas."""
        pass
