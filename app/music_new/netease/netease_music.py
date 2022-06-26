from time import time as now
from typing import Optional

from app.music_new.music import MusicPiece, Platform, CachedRequestor
from app.music_new.netease.apis import *


class NeteaseMusicPlatform(Platform):
    def __init__(self):
        super(NeteaseMusicPlatform, self).__init__('netease', 'netease-music', '网易', '网易云', '网易云音乐')


class SourceRequestor(CachedRequestor):
    def __init__(self, song_id: int):
        super(SourceRequestor, self).__init__(expiration_time_sec=5 * 60)
        self.song_id = song_id

    async def _invoke(self) -> Optional[str]:
        urls = await batch_fetch_media_urls(self.song_id)
        self.cache = urls.get(self.song_id)
        return self.cache


class DetailRequestor(CachedRequestor):
    def __init__(self, song_id, details: BasicDetails = None):
        super(DetailRequestor, self).__init__()
        self.song_id = song_id
        if details is not None:
            self.cache = details
            self.lastrun_sec = now()

    async def _invoke(self) -> BasicDetails:
        details = await batch_fetch_basic_details(self.song_id)
        if details.get(self.song_id) is not None:
            self.cache = details[self.song_id]
            return self.cache
        else:
            raise Exception(f'no music found corresponding to id {self.song_id}.')


class NeteaseMusic(MusicPiece):
    def __init__(self, song_id, details: BasicDetails = None):
        super().__init__(NeteaseMusicPlatform, [
            SourceRequestor(song_id),
            DetailRequestor(song_id, details)
        ])

    @property
    async def name(self) -> str:
        details: BasicDetails = await self.requestors[DetailRequestor.__name__]()
        return details.name

    @property
    async def artists(self) -> list[str]:
        details: BasicDetails = await self.requestors[DetailRequestor.__name__]()
        return details.artists

    @property
    async def duration_ms(self) -> int:
        details: BasicDetails = await self.requestors[DetailRequestor.__name__]()
        return details.duration_ms

    @property
    async def cover_url(self) -> str:
        details: BasicDetails = await self.requestors[DetailRequestor.__name__]()
        return details.cover_url

    @property
    async def playable(self) -> bool:
        url: Optional[str] = await self.requestors[SourceRequestor.__name__]()
        return url is not None

    @property
    async def media_url(self) -> Optional[str]:
        url: Optional[str] = await self.requestors[SourceRequestor.__name__]()
        return url
