import aiohttp
import re

from loguru import logger

from app.music.music import Music
from app.music.netease.details import song_ids_to_instances

NETEASE_PLAYLIST_API = "https://music.163.com/playlist/"
NETEASE_PLAYLIST_SONG_ID_PATTERN = re.compile(r'<li><a href="/song\?id=(.*?)">(.*?)</a></li>')


async def fetch_music_ids_by_playlist_id(playlist_id: str) -> list[str]:
    url = f"{NETEASE_PLAYLIST_API}?id={playlist_id}"
    music_ids = []

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            response = await r.text()
            matches = NETEASE_PLAYLIST_SONG_ID_PATTERN.findall(response)
            if not matches:
                raise Exception(f"无法查询到歌单: {playlist_id} 中的歌曲, 请检查你的输入")
            else:
                for this_music in matches:
                    music_ids.append(this_music[0])
    return music_ids

async def fetch_music_list_by_id(playlist_id: str) -> list[Music]:
    music_ids = await fetch_music_ids_by_playlist_id(playlist_id=playlist_id)
    result = await song_ids_to_instances(*music_ids)

    logger.debug(f"{result}")
    return result

if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(fetch_music_list_by_id("7264605431"))
