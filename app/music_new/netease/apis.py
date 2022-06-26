import json
from typing import NamedTuple

import aiohttp

NETEASE_MUSIC_DETAIL_URL = 'https://music.163.com/api/song/detail/'
NETEASE_MUSIC_MEDIA_URL = 'https://music.163.com/api/song/enhance/player/url/'
NETEASE_MUSIC_DEFAULT_BITRATE = 320_000


class BasicDetails(NamedTuple):
    name: str
    artists: list[str]
    duration_ms: int
    cover_url: str


async def batch_fetch_basic_details(*song_ids: int) -> dict[int, BasicDetails]:
    """Incorrect id does not have a corresponding song entry in the returned value."""
    async with aiohttp.ClientSession() as sess:
        async with sess.get(NETEASE_MUSIC_DETAIL_URL, params={
            'ids': f'[{",".join(map(str, song_ids))}]'
        }) as resp:
            text = await resp.text()
            data = json.loads(text)
            status = data.get('code', 404)
            if status == 200:
                return {
                    song['id']: BasicDetails(
                        song.get('name', 'N/A'),
                        [artist.get('name', 'Unknown') for artist in song.get('artists', [])],
                        song.get('duration', 0),
                        song.get("album", {}).get("picUrl", "") + '?param=130y130'
                    ) for song in data.get('songs', []) if isinstance(song.get('id'), int)
                }
            else:
                raise Exception(data.get('error', f'fetch music details failed with ids {song_ids}, code is {status}.'))


async def batch_fetch_media_urls(*song_ids: int) -> dict[int, str]:
    """Incorrect id does not have a corresponding song entry in the returned value."""
    async with aiohttp.ClientSession() as sess:
        async with sess.get(NETEASE_MUSIC_MEDIA_URL, params={
            'br': NETEASE_MUSIC_DEFAULT_BITRATE,
            'ids': f'[{",".join(map(str, song_ids))}]'
        }) as resp:
            text = await resp.text()
            data = json.loads(text)
            status = data.get('code', 403)
            if status == 200:
                return {
                    song['id']: song['url'] for song in data.get('data', [])
                    if isinstance(song.get('id'), int) and isinstance(song.get('url'), str)
                }
            else:
                raise Exception(data.get('error', f'fetch media urls failed with ids {song_ids}, code is {status}.'))
