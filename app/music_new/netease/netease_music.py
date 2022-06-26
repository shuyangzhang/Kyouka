import json
from typing import Optional

import aiohttp

from app.music_new.music import MusicPiece, Platform, PropertyRequestor


class NeteaseMusicPlatform(Platform):
    def __init__(self):
        super(NeteaseMusicPlatform, self).__init__('netease', 'netease-music', '网易', '网易云', '网易云音乐')


class SourceRequestor(PropertyRequestor):
    def __init__(self, song_id: int):
        super(SourceRequestor, self).__init__(expiration_time_sec=5 * 60)
        self.song_id = song_id

    async def __invoke(self):
        async with aiohttp.ClientSession() as sess:
            async with sess.post('https://music.163.com/api/song/enhance/player/url/', params={
                'br': '3200000',
                'Aids': f'[{self.song_id}]'
            }) as resp:
                text = await resp.text()
                data = json.loads(text)
                return data


class DetailRequestor(PropertyRequestor):
    def __init__(self, song_id: int):
        super(DetailRequestor, self).__init__()
        self.song_id = song_id

    async def __invoke(self):
        async with aiohttp.ClientSession() as sess:
            async with sess.post('https://music.163.com/api/song/detail/', params={
                'ids': f'[{self.song_id}]'
            }) as resp:
                text = await resp.text()
                data = json.loads(text)
                return data


class NeteaseMusic(MusicPiece):
    def __init__(self, song_id):
        super().__init__(NeteaseMusicPlatform, [
            SourceRequestor(song_id),
            DetailRequestor(song_id)
        ])
        self.song_id = song_id
        self.__name: Optional[str] = None
        self.__artists: Optional[list[str]] = None
        self.__playable: Optional[bool] = None
        self.__duration_ms: Optional[int] = None
        self.__cover_url: Optional[str] = None

    @property
    async def name(self) -> str:
        if self.__name is None:
            data = await self.requestors['DetailRequestor']()
            self.__name = data.get('songs', [{}])[0].get('name', 'N/A')
        return self.__name

    @property
    async def artists(self) -> list[str]:
        if self.artists is None:
            data = await self.requestors['DetailRequestor']()
            artists = data.get('songs', [{}])[0].get('artists', [])
            self.__artists = [artists.get('name', 'Unknown') for artist in artists]
        return self.__artists

    @property
    async def media_url(self) -> str:
        return await self.requestors['SourceRequestor']()


async def main():
    music = NeteaseMusic(36226134)
    print(repr(music))
    print(await music.media_url)
    print(await asyncio.gather(music.name, music.artists))


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
