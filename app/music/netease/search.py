from typing import Optional

import aiohttp
from loguru import logger

from app.music.music import Music
from app.music.netease.details import song_ids_to_instances

NETEASE_API = "http://cloud-music.pl-fe.cn/"


async def fetch_music_source_by_name(music_name: str) -> Optional[Music]:
    url = f"{NETEASE_API}search?keywords={music_name}&limit=1&offset=0&type=1"
    ret = None

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            resp_json = await r.json()
            status = resp_json.get("code", 500)
            if status == 500:
                raise Exception(resp_json.get("error", "fetch music source failed, unknown reason."))
            else:
                data = resp_json.get("result", {}).get("songs", [])
                if data:
                    musics = await song_ids_to_instances(data[0].get('id'))
                    ret = musics[0] if musics else None

    logger.debug(f'FETCHED: {str(ret)}')
    return ret


async def search_music_by_keyword(music_name: str, limit: int = 5) -> list[Music]:
    url = f"{NETEASE_API}search?keywords={music_name}&limit={limit}&offset=0&type=1"
    ret = None

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            resp_json = await r.json()
            status = resp_json.get("code", 500)
            if status != 200:
                raise Exception(resp_json.get("error", "fetch music source failed, unknown reason."))
            else:
                data = resp_json.get("result", {}).get("songs", [])
                if data:
                    ret = await song_ids_to_instances(*[song['id'] for song in data])

    logger.debug(f'FETCHED: {str(ret)}')
    return ret



if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(search_music_by_keyword("篇章"))
