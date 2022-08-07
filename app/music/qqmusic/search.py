import json
import aiohttp
from loguru import logger
from khl import Bot
from app.music.music import Music
from app.utils.asset_utils import webp2jpeg


# QQMUSIC_SEARCH_API = "https://c.y.qq.com/soso/fcgi-bin/client_search_cp?p=1&w="
# QQ音乐客户端抓包获得
QQMUSIC_CLIENT_SEARCH_API = "https://u.y.qq.com/cgi-bin/musicu.fcg"
QQMUSIC_CLIENT_SONG_API = "https://u.y.qq.com/cgi-bin/musicu.fcg"
# QQMUSIC_SONG_API = "https://u.y.qq.com/cgi-bin/musicu.fcg?data="
QQMUSIC_SONG_BASICURL = "http://dl.stream.qqmusic.qq.com/"
# QQMUSIC_SONG_DETAILBASIC = "https://y.qq.com/n/ryqq/songDetail/"
QQMUSIC_SONG_COVER = "http://y.qq.com/music/photo_new/T00{singerOrMusic}R300x300M000{id}.jpg"

async def get_song_mid(songName: str):
    # 构造查询请求
    query_data = {
        "music.search.SearchCgiService": {
            "method": "DoSearchForQQMusicDesktop",
            "module": "music.search.SearchCgiService",
            "param": {
                "num_per_page": 5,
                "page_num": 1,
                "query": songName,
                "search_type": 0
            }
        }
    }
    # 关键字查询歌曲
    async with aiohttp.ClientSession() as session:
        async with session.post(QQMUSIC_CLIENT_SEARCH_API, data=json.dumps(query_data, ensure_ascii=False)) as resp:
            song_list = json.loads((await resp.text())).get("music.search.SearchCgiService").get("data", {}).get("body", {}).get("song", {}).get("list", [])
            matched = []
            for song_info in song_list:
                if(song_info.get("action", {}).get("alert", 0) == 0):
                    continue
                singer_list = song_info.get("singer", [{"name": "未知歌手"}])
                singers = ""
                for singer in singer_list:
                    singers += singer.get("name", "") + "&"
                singers = singers[:-1]
                # 处理封面ID
                if(song_info.get("album", {}).get("mid","") == ""):
                    song_info["albummid"] = "1"+song_info.get("singer", [])[0].get("mid", "")
                else:
                    song_info["albummid"] = "2"+song_info.get("album", {}).get("mid","")
                matched.append(
                    {
                        "song_id": song_info.get("mid", ""),
                        "song_name": song_info.get("name", ""),
                        "singers": singers,
                        "song_interval": song_info.get("interval", 0) * 1000,
                        "album_id": song_info.get("albummid", ""),
                        "album_name": song_info.get("album", {}).get("name", "未知专辑")
                    }
                )
    return matched

async def handle_informations(bot: Bot, matched: list):
    result = []
    for song_info in matched:
        # 歌曲链接查询请求构造
        get_song_data = {
            "vkey.GetVkeyServer": {
            "method": "CgiGetVkey",
            "module": "vkey.GetVkeyServer",
            "param": {
                    "guid": "0",
                    "songmid": [
                        song_info["song_id"]
                    ],
                    "uin": "0"
                }
            }
        }
        # 获取歌曲链接
        async with aiohttp.ClientSession() as session:
            async with session.post(QQMUSIC_CLIENT_SONG_API, data=json.dumps(get_song_data, ensure_ascii=False)) as response:
                m4aUrl = QQMUSIC_SONG_BASICURL+((await response.json(content_type="text/plain")).get("vkey.GetVkeyServer", {}).get("data", {}).get("midurlinfo", [])[0].get("purl", ""))

            # 封面链接生成
            kwargs = {"singerOrMusic": song_info["album_id"][0], "id": song_info["album_id"][1:]}
            async with session.get(QQMUSIC_SONG_COVER.format(**kwargs)) as response:
                if(response.status == 404):
                    cover_url = "http://y.qq.com/mediastyle/global/img/album_300.png"
                else:
                    cover_url_webp = QQMUSIC_SONG_COVER.format(**kwargs)
                    cover_url = await webp2jpeg(bot, cover_url_webp)

            result.append(Music(song_info["song_id"], song_info["song_name"], song_info["singers"], m4aUrl, song_info["song_interval"], song_info["album_name"], cover_url, "qqmusic"))

    # logger.debug(f"{[str(x) for x in result]}")
    return result

async def qsearch_music_by_keyword(bot, songName):
    matched = await get_song_mid(songName)
    return (await handle_informations(bot, matched))
