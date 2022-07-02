import json
import math
import re
from dataclasses import dataclass
from enum import Enum
from time import time as now
from typing import Optional

import aiohttp

from app.music_new.music import Platform, MusicPiece

MUSIC_ID_PATTERN = re.compile(r'[1-9]\d*')
MUSIC_URL_PATTERN = re.compile(
    r'((https?)://)?music\.163\.com/'
    r'(song/(?P<id1>[1-9]\d*))'
    r'|(#/song\?(.*?&)*id=(?P<id2>[1-9]\d*))'
)

NETEASE_MUSIC_DETAIL_URL = 'http://music.163.com/api/song/detail/'
NETEASE_MUSIC_MEDIA_URL = 'http://music.163.com/api/song/enhance/player/url/'
NETEASE_MUSIC_DEFAULT_BITRATE = 320_000
NETEASE_MUSIC_SEARCH_URL = 'http://music.163.com/api/search/get/'


@dataclass
class BasicDetails:
    song_id: int
    name: str
    artists: list[str]
    duration_ms: int
    cover_url: str


class SearchType(Enum):
    MUSIC = 1
    ALBUM = 10
    SINGER = 100
    PLAYLIST = 1000
    USER = 1002
    MV = 1004
    LYRICS = 1006
    RADIO = 1009
    VIDEO = 1014


async def search_music(sess: aiohttp.ClientSession, keywords: str, limit: int = 30, offset: int = 0) \
        -> list[BasicDetails]:
    async with sess.get(NETEASE_MUSIC_SEARCH_URL, params={
        's': keywords,
        'type': SearchType.MUSIC.value,
        'limit': limit,
        'offset': offset
    }) as resp:
        text = await resp.text()
        data = json.loads(text)
        status = data.get('code')
        if status == 200:
            return [
                BasicDetails(
                    song_id=song['id'],
                    name=song.get('name', 'N/A'),
                    artists=[artist.get('name', 'Unknown') for artist in song.get('artists', [])],
                    duration_ms=song.get('duration', 0),
                    cover_url=song.get("album", {}).get("picUrl", "") + '?param=130y130'
                ) for song in data.get('result', {}).get('songs', []) if isinstance(song.get('id'), int)
            ]
        else:
            raise Exception(f"could not search music with keywords '{keywords}', code is: {status}")


async def batch_fetch_basic_details(sess: aiohttp.ClientSession, *song_ids: int) -> dict[int, BasicDetails]:
    """Incorrect id does not have a corresponding song entry in the returned value."""
    async with sess.get(NETEASE_MUSIC_DETAIL_URL, params={
        'ids': f'[{",".join(map(str, song_ids))}]'
    }) as resp:
        text = await resp.text()
        data = json.loads(text)
        status = data.get('code')
        if status == 200:
            return {
                song['id']: BasicDetails(
                    song_id=song['id'],
                    name=song.get('name', 'N/A'),
                    artists=[artist.get('name', 'Unknown') for artist in song.get('artists', [])],
                    duration_ms=song.get('duration', 0),
                    cover_url=song.get("album", {}).get("picUrl", "") + '?param=130y130'
                ) for song in data.get('songs', []) if isinstance(song.get('id'), int)
            }
        else:
            raise Exception(f"could not fetch music details with ids {song_ids}, code is: {status}")


async def batch_fetch_media_urls(sess: aiohttp.ClientSession, *song_ids: int,
                                 bitrate=NETEASE_MUSIC_DEFAULT_BITRATE) -> dict[int, str]:
    """Incorrect id does not have a corresponding song entry in the returned value."""
    async with sess.get(NETEASE_MUSIC_MEDIA_URL, params={
        'br': bitrate,
        'ids': f'[{",".join(map(str, song_ids))}]'
    }) as resp:
        text = await resp.text()
        data = json.loads(text)
        status = data.get('code')
        if status == 200:
            return {
                song['id']: song['url'] for song in data.get('data', [])
                if isinstance(song.get('id'), int) and isinstance(song.get('url'), str)
            }
        else:
            raise Exception(f'could not fetch media urls with ids {song_ids}, code is {status}.')


class NeteaseMusicPlatform(Platform):
    def __init__(self):
        super(NeteaseMusicPlatform, self).__init__('netease', 'netease-music', '网易', '网易云', '网易云音乐')

    async def search_music(self, sess: aiohttp.ClientSession, keywords: str, limit: int) -> list[MusicPiece]:
        pass

    @staticmethod
    def is_music_id(text: str):
        return MUSIC_ID_PATTERN.fullmatch(text) is not None

    @staticmethod
    def is_music_url(text: str):
        return MUSIC_URL_PATTERN.fullmatch(text) is not None

    async def play_by_url(self, sess: aiohttp.ClientSession, url: str) -> Optional[MusicPiece]:
        result = MUSIC_URL_PATTERN.fullmatch(url)
        if result is None:
            return None
        result = result.groupdict()
        result = result.get('id1') or result.get('id2')
        if result is None:
            return None
        return await self.play_by_id(sess, int(result))

    async def play_by_id(self, sess: aiohttp.ClientSession, music_id: int) -> Optional[MusicPiece]:
        details = await batch_fetch_basic_details(sess, music_id)
        detail = details.get(music_id)
        return None if detail is None else NeteaseMusic(detail)

    async def import_playlist_by_url(self, sess: aiohttp.ClientSession, url: str, limit: int, offset: int = 0) \
            -> Optional[MusicPiece]:
        pass

    async def import_album_by_url(self, sess: aiohttp.ClientSession, url: str, limit: int, offset: int = 0) \
            -> Optional[MusicPiece]:
        pass


MEDIA_EXPIRATION_TIME_SEC = 5 * 60


class NeteaseMusic(MusicPiece):
    def __init__(self, details: BasicDetails):
        super(NeteaseMusic, self).__init__(details.name, details.artists)
        self.details = details
        self.__media_expiration_sec = -math.inf
        self.__media_url = None

    async def cover_url(self, sess: aiohttp.ClientSession) -> str:
        return self.details.cover_url

    async def duration_ms(self, sess: aiohttp.ClientSession) -> int:
        return self.details.duration_ms

    async def media_url(self, sess: aiohttp.ClientSession) -> Optional[str]:
        if self.__media_expiration_sec < now():
            urls = await batch_fetch_media_urls(sess, self.details.song_id)
            self.__media_url = urls.get(self.details.song_id)
            self.__media_expiration_sec = now() + MEDIA_EXPIRATION_TIME_SEC
        return self.__media_url
