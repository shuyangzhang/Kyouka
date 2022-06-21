import re

import aiohttp
from loguru import logger

from app.music.music import Music
from app.music.netease.details import song_ids_to_instances

NETEASE_ALBUM_API = 'https://music.163.com/album'
NETEASE_ALBUM_SONG_ID_PATTERN = re.compile(r'<li><a href="/song\?id=(\d+)".*?>.*?</a></li>')


async def fetch_music_ids_by_album_id(album_id: str) -> list[str]:
    url = f'{NETEASE_ALBUM_API}?id={album_id}'

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            response = await r.text()
            matches = NETEASE_ALBUM_SONG_ID_PATTERN.findall(response)
            if not matches:
                raise Exception(f'无法查询到专辑: {album_id} 中的歌曲, 请检查你的输入')
            else:
                return matches
    return []


async def fetch_album_by_id(album_id: str) -> list[Music]:
    music_ids = await fetch_music_ids_by_album_id(album_id=album_id)
    result = await song_ids_to_instances(*music_ids)

    logger.debug(f'{result}')
    return result
