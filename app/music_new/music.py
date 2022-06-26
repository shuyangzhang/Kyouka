import math
import time
from abc import abstractmethod as abstract, ABC as ABSTRACT
from asyncio.locks import Lock
from typing import Optional, Type


class MusicPiece(ABSTRACT):
    """The abstract class for music in a single platform.
    If one day we need music playable from multiple platforms, then build a CompositeMusic class :)

    Most properties are essentially getters thus we can perform lazy loading.
    Online resources that can expire (e.g. playable media links) should be re-obtained when necessary.

    Fetching multiple properties may lead to race condition. Avoid them while coding with a lock.
    """

    def __init__(self, platform: Type['Platform'], requestors: list['PropertyRequestor']):
        self.platform = platform
        self.requestors: dict[str, 'PropertyRequestor'] = {}
        self.endtime_ms: Optional[int] = None

        for r in requestors:
            r.bind(self)
            self.requestors[r.name] = r

    @property
    @abstract
    async def name(self) -> str:
        pass

    @property
    @abstract
    async def artists(self) -> list[str]:
        pass

    @property
    @abstract
    async def playable(self) -> bool:
        pass

    @property
    @abstract
    async def media_url(self) -> str:
        pass

    @property
    @abstract
    async def duration_ms(self) -> int:
        pass

    @property
    @abstract
    async def cover_url(self) -> str:
        pass

    def __repr__(self):
        return f'<{self.__class__.__name__} with attributes {self.__dict__}>'

    class PropertyRequestor(ABSTRACT):
        def __init__(self, name: str = None, expiration_time_sec: float = math.inf):
            self.name = name or self.__class__.__name__
            self.expiration_time_sec = expiration_time_sec
            self.owner: Optional[MusicPiece] = None
            self.lock = Lock()
            self.cache = None
            self.__counter = 0  # for profiling
            self.lastrun_sec = -math.inf

        def bind(self, music: 'MusicPiece'):
            self.owner = music

        @abstract
        async def __invoke(self) -> any:
            pass

        async def __call__(self) -> any:
            async with self.lock:
                if time.time() - self.lastrun_sec > self.expiration_time_sec or self.__counter == 0:
                    self.__counter += 1
                    self.lastrun_sec = time.time()
                    self.result = await self.invoke()
            return self.result

        def __repr__(self):
            return f'<{self.__class__.__name__} with attributes {self.__dict__}>'


PropertyRequestor = MusicPiece.PropertyRequestor


class Platform(ABSTRACT):
    """The abstract class for a music platform.

    Some platforms may have additional feature (e.g. radio of netease).
    What we should do is create another platform with different implementation.
    Methods not implemented should be discovered by checking the @abstract annotation.
    """

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
        pass

    async def play_by_keywords(self, keywords: str, limit: int) -> Optional[MusicPiece]:
        result = await self.search_music(keywords, limit)
        return result[0] if result else None

    @abstract
    async def play_by_url(self, url: str) -> Optional[MusicPiece]:
        """A music can have multiple urls, which potentially come from phone app, PC client and webpage."""
        pass

    @abstract
    async def play_by_id(self, music_id: int):
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
