import json
import aiohttp
from loguru import logger
from khl import Bot
from app.music.music import Music
from app.utils.asset_utils import webp2jpeg


QQMUSIC_SEARCH_API = "https://c.y.qq.com/soso/fcgi-bin/client_search_cp?p=1&w="
QQMUSIC_SONG_API = "https://u.y.qq.com/cgi-bin/musicu.fcg?data="
QQMUSIC_SONG_BASICURL = "http://dl.stream.qqmusic.qq.com/"
QQMUSIC_SONG_DETAILBASIC = "https://y.qq.com/n/ryqq/songDetail/"
QQMUSIC_SONG_COVER = "http://y.qq.com/music/photo_new/T00{singerOrMusic}R300x300M000{id}.jpg"


async def get_song_mid(songName: str):
    url = QQMUSIC_SEARCH_API+songName
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return resp.status
            h_dict = json.loads((await resp.text())[9:-1])
            matched = []
            song_list = h_dict.get("data", {}).get("song", {}).get("list", [])
            for song_info in song_list:
                if(song_info.get("alertid", 0) == 0):
                    continue
                singer_list = song_info.get("singer", [{"name": "未知歌手"}])
                singers = ""
                for singer in singer_list:
                    singers += singer.get("name", "") + "&"
                singers = singers[:-1]
                if(song_info.get("albummid", "") == ""):
                    song_info["albummid"] = "1"+song_info.get("singer", [])[0].get("mid", "")
                else:
                    song_info["albummid"] = "2"+song_info.get("albummid", "")
                matched.append((song_info.get("songmid", ""), song_info.get("songname", ""), singers, song_info.get("interval", 0) * 1000, song_info.get("albummid", ""), song_info.get("albumname", '未知专辑')))
    return matched

async def handle_informations(bot: Bot, matched: list):
    result = []
    guid, uin = "0", "0"
    for song_info in matched:
        songmid = song_info[0]
        p_url = QQMUSIC_SONG_API+f'{{"req":{{"param": {{"guid": "{guid}"}}}}, "req_0": {{"module": "vkey.GetVkeyServer", "method": "CgiGetVkey", "param": {{"guid": "{guid}", "songmid": ["{songmid}"], "uin": "{uin}"}}}}, "comm": {{"uin": {uin}}}}}'
        async with aiohttp.ClientSession() as session:
            async with session.get(p_url) as response:
                m4aUrl = QQMUSIC_SONG_BASICURL+((await response.json(content_type="text/plain")).get("req_0", {}).get("data", {}).get("midurlinfo", [])[0].get("purl", ""))

            kwargs = {"singerOrMusic": song_info[4][0], "id": song_info[4][1:]}
            async with session.get(QQMUSIC_SONG_COVER.format(**kwargs)) as response:
                if(response.status == 404):
                    cover_url = "http://y.qq.com/mediastyle/global/img/album_300.png"
                else:
                    cover_url_webp = QQMUSIC_SONG_COVER.format(**kwargs)
                    cover_url = await webp2jpeg(bot, cover_url_webp)

            result.append(Music(song_info[0], song_info[1], song_info[2], m4aUrl, song_info[3], song_info[5], cover_url, 'qqmusic'))
            if len(result) == 5:
                break

    logger.debug(f"{[str(x) for x in result]}")
    return result

async def qsearch_music_by_keyword(bot, songName):
    matched = await get_song_mid(songName)
    if isinstance(matched, int):
        raise Exception(f'qq音乐搜索失败({matched})')
    return (await handle_informations(bot, matched))


if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete((qsearch_music_by_keyword("Igallta")))
