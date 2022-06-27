import math
import re
from time import time as now

from app.music_new.music import *
from app.music_new.netease.apis import *


MUSIC_ID_PATTERN = re.compile(r'[1-9]\d*')
MUSIC_URL_PATTERN = re.compile(
    r'((https?)://)?music\.163\.com/'
    r'(song/(?P<id1>[1-9]\d*))'
    r'|(#/song\?(.*?&)*id=(?P<id2>[1-9]\d*))'
)


class NeteaseMusicPlatform(Platform):
    def __init__(self):
        super(NeteaseMusicPlatform, self).__init__('netease', 'netease-music', '网易', '网易云', '网易云音乐')

    async def search_music(self, keywords: str, limit: int) -> list[MusicPiece]:
        pass

    @staticmethod
    def is_music_id(text: str):
        return MUSIC_ID_PATTERN.fullmatch(text) is not None

    @staticmethod
    def is_music_url(text: str):
        return MUSIC_URL_PATTERN.fullmatch(text) is not None

    async def play_by_url(self, url: str) -> Optional[MusicPiece]:
        result = MUSIC_URL_PATTERN.fullmatch(url)
        if result is None:
            return None
        result = result.groupdict()
        result = result.get('id1') or result.get('id2')
        if result is None:
            return None
        return await self.play_by_id(int(result))

    async def play_by_id(self, music_id: int) -> Optional[MusicPiece]:
        details = await batch_fetch_basic_details(music_id)
        detail = details.get(music_id)
        return None if detail is None else NeteaseMusic(music_id, detail)

    async def import_playlist_by_url(self, url: str) -> Optional[MusicPiece]:
        pass

    async def import_album_by_url(self, url: str, range_from: int, range_to_inclusive: int) -> Optional[MusicPiece]:
        pass


MEDIA_EXPIRATION_TIME_SEC = 5 * 60


class NeteaseMusic(MusicPiece):
    def __init__(self, song_id: int, details: BasicDetails):
        super(NeteaseMusic, self).__init__(NeteaseMusicPlatform, details.name, details.artists)
        self.song_id = song_id
        self.details = details
        self.__media_expiration_sec = -math.inf
        self.__media_url = None

    @property
    async def cover_url(self) -> str:
        return self.details.cover_url

    @property
    async def duration_ms(self) -> int:
        return self.details.duration_ms

    @property
    async def media_url(self) -> Optional[str]:
        if self.__media_expiration_sec < now():
            urls = await batch_fetch_media_urls(self.song_id)
            self.__media_url = urls.get(self.song_id)
            self.__media_expiration_sec = now() + MEDIA_EXPIRATION_TIME_SEC
        return self.__media_url
