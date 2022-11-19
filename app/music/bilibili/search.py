from typing import Optional

import aiohttp
from loguru import logger

from app.music.music import Music
from app.config.common import settings

BILIBILI_VIDEO_INFO_API = "http://api.bilibili.com/x/web-interface/view"
BILIBILI_AUDIO_SOURCE_API = "https://api.bilibili.com/x/player/playurl"
BILIBIlI_VIDEO_SEARCH_API = "https://api.bilibili.com/x/web-interface/search/type?keyword={KWD}&search_type=video&page_size={SEARCH_NUM}"

BPROXY_API = "https://bproxy.shuyangzhang.repl.co/"

BOT_HEADERS = {
    "User-Agent": "Kyouka Music Player/1.0.0(triint@qq.com)"
}

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
                    cover_image_url = data.get("pic", "")
                else:
                    matched = False
                    name = ""
                    author = ""
                    cid = 0
                    duration = 0
                    cover_image_url = ""
    logger.debug(f"{[matched, name, author, cid, duration, cover_image_url]}")
    return matched, name, author, cid, duration, cover_image_url

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
    matched, name, author, cid, duration, cover_image_url = await fetch_basic_video_info_by_BVid(BVid=BVid)
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

async def search_bvideo_by_title(Keyword: str, Video_num: int = 5):
    url = BILIBIlI_VIDEO_SEARCH_API.format(KWD=Keyword, VIDEO_NUM=Video_num+1)
    res = []
    async with aiohttp.ClientSession(headers=BOT_HEADERS) as session:
        async with session.get(url) as r:
            resp_json = await r.json()
            status = resp_json.get("code", 1)
            if status != 0:
                raise Exception(resp_json.get("message", "search video info failed, unknown reason.")+" with code: "+str(status))
            else:
                data = resp_json.get("data", {}).get("result", [])
                for da in data:
                    if(da.get("bvid", None) != None):  res.append(da.get("bvid", None))
    if(res == []):
        logger.debug("find no video with title: {title}".format(title=Keyword))
        raise Exception("didn't find any video with title: {title}".formaat(title=Keyword))
    return res

async def bvid_to_music_by_local_bproxy(BVid: str) -> Optional[Music]:
    ret = await bvid_to_music(BVid=BVid)
    ret.source = f"{settings.local_bproxy_url}/{BVid}"
    logger.debug(f"FETCHED: {str(ret)}")
    return ret

if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(bvid_to_music_by_bproxy("BV1Jb411U7u2"))
