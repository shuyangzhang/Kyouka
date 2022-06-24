import json

import aiohttp

from app.music_new.music import MusicPiece, Platform, PropertyRequestor


class NeteaseMusicPlatform(Platform):
    def __init__(self):
        super(NeteaseMusicPlatform, self).__init__('netease', 'netease-music', '网易', '网易云', '网易云音乐')


class SourceRequestor(PropertyRequestor):
    def __init__(self, song_id: int):
        super(SourceRequestor, self).__init__(expiration_time_sec=5 * 60)
        self.song_id = song_id

    async def invoke(self, *args, **kwargs):
        async with aiohttp.ClientSession() as sess:
            async with sess.post('https://music.163.com/api/song/enhance/player/url/', params={
                'br': '3200000',
                'ids': f'[{self.song_id}]'
            }) as resp:
                text = await resp.text()
                data = json.loads(text)
                return data.get('data', [{}])[0].get('url')


class DetailRequestor(PropertyRequestor):
    def __init__(self, song_id: int):
        super(DetailRequestor, self).__init__()
        self.song_id = song_id

    async def invoke(self, *args, **kwargs):
        async with aiohttp.ClientSession() as sess:
            async with sess.post('https://music.163.com/api/song/detail/', params={
                'ids': f'[{self.song_id}]'
            }) as resp:
                text = await resp.text()
                data = json.loads(text)
                song = data.get('songs', [{}])[0]
                return song


class NeteaseMusic(MusicPiece):
    def __init__(self, song_id):
        super().__init__(NeteaseMusicPlatform, [
            SourceRequestor(song_id),
            DetailRequestor(song_id)
        ])
        self.song_id = song_id

    @property
    async def name(self) -> str:
        song = await self.requestors['DetailRequestor']('name')
        return song['name']

    @property
    async def artists(self) -> list[str]:
        song = await self.requestors['DetailRequestor']('artist')
        return [artist['name'] for artist in song['artists']]

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
