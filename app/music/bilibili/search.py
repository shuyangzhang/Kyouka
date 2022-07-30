from typing import Optional

import aiohttp
from loguru import logger

from app.music.music import Music

BILIBILI_VIDEO_INFO_API = "http://api.bilibili.com/x/web-interface/view"
BILIBILI_AUDIO_SOURCE_API = "https://api.bilibili.com/x/player/playurl"

BPROXY_API = "https://bproxy.shuyangzhang.repl.co/"


async def fetch_basic_video_info_by_BVid(BVid: str):
    url = f"{BILIBILI_VIDEO_INFO_API}?bvid={BVid}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            resp_json = await r.json()
            status = resp_json.get("code", 1)
            if status != 0:
                raise Exception(resp_json.get("message", "fetch video info failed, unknown reason."))
            else:
                data = resp_json.get("data", {})
                if data:
                    matched = True
                    name = data.get("title", "未知视频")
                    author = data.get("owner", {}).get("name", "未知up主")
                    cid = data.get("cid", 0)
                    duration = data.get("duration", 180)  # seconds
                    duration *= 1000
                else:
                    matched = False
                    name = ""
                    author = ""
                    cid = 0
                    duration = 0
    logger.debug(f"{[matched, name, author, cid, duration]}")
    return matched, name, author, cid, duration

async def fetch_audio_source_by_BVid_and_cid(BVid: str, cid: int):
    url = f"{BILIBILI_AUDIO_SOURCE_API}?bvid={BVid}&cid={cid}&qn=16&fnval=80"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            resp_json = await r.json()
            status = resp_json.get("code", 1)
            if status != 0:
                raise Exception(resp_json.get("message", "fetch audio source failed, unknown reason."))
            else:
                data = resp_json.get("data", {})
                if data:
                    matched = True
                    dash = data.get("dash", {})
                    audio = dash.get("audio", [])
                    if not audio:
                        raise Exception("empty audio source")
                    else:
                        source = audio[0].get("base_url", "")
                else:
                    matched = False
                    source = ""
    logger.debug(f"{[matched, source]}")
    return matched, source

async def bvid_to_music(BVid: str) -> Optional[Music]:
    ret = None
    matched, name, author, cid, duration = await fetch_basic_video_info_by_BVid(BVid=BVid)
    if matched:
        matched, source = await fetch_audio_source_by_BVid_and_cid(BVid=BVid, cid=cid)
        ret = Music(BVid, name, author, source, duration, '', '', 'bili')

    logger.debug(f'FETCHED: {str(ret)}')
    return ret

async def bvid_to_music_by_bproxy(BVid: str) -> Optional[Music]:
    url = f"{BPROXY_API}bproxy?bvid={BVid}"
    ret = None

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            resp_json = await r.json()
            status = resp_json.get("status", {}).get("status_code", 500)
            if status == 500:
                raise Exception(resp_json.get("status", {}).get("msg", "fetch bproxy failed, unknown reason."))
            else:
                data = resp_json.get("data", {})
                if data:
                    ret = Music(
                        BVid,
                        data.get('name', ''),
                        data.get('author', ''),
                        data.get('source'),
                        data.get('duration', 180000),
                        '',
                        data.get('cover_image_url', ''),
                        'bili'
                    )
    logger.debug(f'FETCHED: {str(ret)}')
    return ret

if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(bvid_to_music_by_bproxy("BV1Jb411U7u2"))
