from abc import abstractmethod as abstract, ABC as ABSTRACT
from typing import Optional, Type


class MusicPiece(ABSTRACT):
    def __init__(self, platform: Type['Platform'], name: str, artists: list[str]):
        self.platform = platform
        self.name = name or 'N/A'
        self.artists = artists or ['Unknown']
        self.endtime_ms: Optional[int] = None

    @property
    @abstract
    async def cover_url(self) -> str:
        pass

    @property
    @abstract
    async def duration_ms(self) -> int:
        pass

    @property
    async def playable(self) -> bool:
        return (await self.media_url) is not None

    @property
    @abstract
    async def media_url(self) -> Optional[str]:
        """Must be consistent with the self.playable: return None when self.playable is False"""
        pass

    def __repr__(self):
        return f'{self.__class__.__name__}({self.platform.__name__}, {repr(self.name)}, {repr(self.artists)})'


class Platform(ABSTRACT):
    """The abstract class for a music platform.

    Some platforms may have additional feature (e.g. radio of netease).
    What we should do is to create another platform with different implementation.

    Do raise NotImplementedError and update __functionalities__ when some functionalities are not available.
    """

    __functionalities__ = [
        'search_music',
        'play_by_keywords',
        'play_by_url',
        'play_by_id',
        'import_album_by_url',
        'import_playlist_by_url'
    ]

    def __init__(self, name: str, *alias: str):
        self.name = name
        self.alias = [*alias]

    def names(self):
        return {self.name, *self.alias}

    # ============================================= Music =============================================

    @abstract
    async def search_music(self, keywords: str, limit: int) -> list[MusicPiece]:
        """Search for at most `limit` musics, but do not get all information at once.
        It can return an empty list."""
        pass

    @staticmethod
    @abstract
    def is_music_url(text: str):
        pass

    @staticmethod
    @abstract
    def is_music_id(text: str):
        """Make it return False if playing by id is not applicable."""
        pass

    async def play_by_keywords(self, keywords: str, limit: int) -> Optional[MusicPiece]:
        result = await self.search_music(keywords, limit)
        return result[0] if result else None

    @abstract
    async def play_by_url(self, url: str) -> Optional[MusicPiece]:
        """A music can have multiple urls, which potentially come from phone app, PC client and webpage."""
        pass

    @abstract
    async def play_by_id(self, music_id: int) -> Optional[MusicPiece]:
        pass

    # ============================================= Album =============================================

    @abstract
    async def import_album_by_url(self, url: str, range_from: int, range_to_inclusive: int) -> Optional[MusicPiece]:
        """An album can have multiple urls, which potentially come from phone app, PC client and webpage."""
        pass

    # ============================================= Playlist =============================================

    @abstract
    async def import_playlist_by_url(self, url: str) -> Optional[MusicPiece]:
        """A playlist can have multiple urls, which potentially come from phone app, PC client and webpage."""
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.name)}, {', '.join(map(repr, self.alias))})"
