from abc import abstractmethod as abstract, ABC as ABSTRACT
from typing import Optional

import aiohttp


class MusicPiece(ABSTRACT):
    def __init__(self, name: str, artists: list[str]):
        self.name = name or 'N/A'
        self.artists = artists or ['Unknown']
        self.endtime_ms: Optional[int] = None

    @abstract
    async def cover_url(self, sess: aiohttp.ClientSession) -> str:
        pass

    @abstract
    async def duration_ms(self, sess: aiohttp.ClientSession) -> int:
        pass

    async def playable(self, sess: aiohttp.ClientSession) -> bool:
        return (await self.media_url(sess)) is not None

    @abstract
    async def media_url(self, sess: aiohttp.ClientSession) -> Optional[str]:
        """Must be consistent with the self.playable: return None when self.playable is False"""
        pass

    def __repr__(self):
        return f'{self.__class__.__name__}({repr(self.name)}, {repr(self.artists)})'


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
    async def search_music(self, sess: aiohttp.ClientSession, keywords: str, limit: int) -> list[MusicPiece]:
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

    async def play_by_keywords(self, sess: aiohttp.ClientSession, keywords: str, limit: int) -> Optional[MusicPiece]:
        result = await self.search_music(sess, keywords, limit)
        return result[0] if result else None

    @abstract
    async def play_by_url(self, sess: aiohttp.ClientSession, url: str) -> Optional[MusicPiece]:
        """A music can have multiple urls, which potentially come from phone app, PC client and webpage."""
        pass

    @abstract
    async def play_by_id(self, sess: aiohttp.ClientSession, music_id: int) -> Optional[MusicPiece]:
        pass

    # ============================================= Album =============================================

    @abstract
    async def import_album_by_url(self, sess: aiohttp.ClientSession, url: str, limit: int, offset: int = 0) \
            -> Optional[MusicPiece]:
        """An album can have multiple urls, which potentially come from phone app, PC client and webpage."""
        pass

    # ============================================= Playlist =============================================

    @abstract
    async def import_playlist_by_url(self, sess: aiohttp.ClientSession, url: str, limit: int, offset: int = 0) \
            -> Optional[MusicPiece]:
        """A playlist can have multiple urls, which potentially come from phone app, PC client and webpage."""
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.name)}, {', '.join(map(repr, self.alias))})"
