import aiohttp
import re
import json

from loguru import logger
from app.music.netease.search import NETEASE_DETAIL_URL, NETEASE_SOURCE_URL
#from search import NETEASE_DETAIL_URL, NETEASE_SOURCE_URL


NETEASE_PLAYLIST_API = "https://music.163.com/playlist/"


async def fetch_music_details_by_id(music_id: str):
    url = f"{NETEASE_DETAIL_URL}?id={music_id}&ids=[{music_id}]"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            resp_json = json.loads(await r.text())     # response is not application/json
            status = resp_json.get("code", 500)
            if status != 200:
                raise Exception(resp_json.get("error", "fetch music details failed, unknown reason."))
            else:
                data = resp_json.get("songs", [])
                if data:
                    matched = True
                    song = data[0]
                    name = song.get("name")
                    vocalist = song.get("artists", [{}])[0].get("name", "未知歌手")
                    source = f"{NETEASE_SOURCE_URL}?id={music_id}.mp3"
                    duration = song.get("duration", 180000)
                    cover_image_url = song.get("album", {}).get("picUrl", "")
                    cover_image_url = f"{cover_image_url}?param=130y130" if cover_image_url else cover_image_url
                else:
                    matched = False
                    name = ""
                    vocalist = ""
                    source = ""
                    duration = 0
                    cover_image_url = ""
    return matched, name, vocalist, source, duration, cover_image_url

async def fetch_music_ids_by_playlist_id(playlist_id: str):
    url = f"{NETEASE_PLAYLIST_API}?id={playlist_id}"
    music_ids = []

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            response = await r.text()
            pattern = '\<li>\<a href="/song\?id=(.*?)">(.*?)</a></li>'
            matches = re.findall(pattern,response)
            if not matches:
                raise Exception(f"无法查询到歌单: {playlist_id} 中的歌曲, 请检查你的输入")
            else:
                for this_music in matches:
                    music_ids.append(this_music[0])
    return music_ids

async def fetch_music_list_by_id(playlist_id: str):
    result = []
    music_ids = await fetch_music_ids_by_playlist_id(playlist_id=playlist_id)
    for this_music_id in music_ids:
        matched, name, vocalist, source, duration, cover_image_url = await fetch_music_details_by_id(music_id=this_music_id)
        if matched:
            result.append([name, vocalist, source, duration, -1, cover_image_url])

    logger.debug(f"{result}")
    return result

if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(fetch_music_list_by_id("7264605431"))
