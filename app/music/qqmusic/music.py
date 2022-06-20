import requests
import json
from loguru import logger

QQMUSIC_SEARCH_API = "https://c.y.qq.com/soso/fcgi-bin/client_search_cp?p=1&w="
QQMUSIC_SONG_API = "https://u.y.qq.com/cgi-bin/musicu.fcg?data="
QQMUSIC_SONG_BASICURL = "http://dl.stream.qqmusic.qq.com/"
QQMUSIC_SONG_DETAILBASIC = "https://y.qq.com/n/ryqq/songDetail/"
QQMUSIC_SONG_COVER = "http://y.qq.com/music/photo_new/T00{0}R300x300M000{1}.jpg"

async def get_song_mid(songName):
    url = QQMUSIC_SEARCH_API+songName
    res = requests.get(url=url)
    h_dict = json.loads(res.text[9:-1])
    matched = []
    song_list = h_dict.get("data", {}).get("song", {}).get("list", [])
    for song_info in song_list:
        if(song_info.get("alterid", 1) == 0):
            continue
        singer_list = song_info.get("singer", ["未知歌手"])
        singers = ""
        for singer_ in singer_list:
            singers += singer_["name"] + "&"
        singers = singers[:-1]
        if(song_info.get("albummid", "") == ""):
            song_info["albummid"] = '1'+song_info.get("singer", "")[0].get("mid", "")
        else:
            song_info["albummid"] = '2'+song_info.get("albummid", "")
        matched.append((song_info.get("songmid", ""), song_info.get("songname", ""), singers, song_info.get("interval", 0)*1000, song_info.get("albummid", "")))
    return matched

async def handle_informations(matched):
    result = []
    guid, uin = "0", "0"
    for song_info in matched:
        songmid = song_info[0]
        p_url = QQMUSIC_SONG_API+f'{{"req":{{"param": {{"guid": "{guid}"}}}}, "req_0": {{"module": "vkey.GetVkeyServer", "method": "CgiGetVkey", "param": {{"guid": "{guid}", "songmid": ["{songmid}"], "uin": "{uin}"}}}}, "comm": {{"uin": {uin}}}}}'
        response = requests.get(url=p_url)
        m4aUrl = QQMUSIC_SONG_BASICURL+response.json().get("req_0", {}).get("data", {}).get("midurlinfo", [])[0].get("purl", "")

        resp = requests.get(QQMUSIC_SONG_COVER.format(song_info[4][0], song_info[4][1:]))
        if(resp.status_code == 404):
            cover_url = "http://y.qq.com/mediastyle/global/img/album_300.png"
        else:
            cover_url = QQMUSIC_SONG_COVER.format(song_info[4][0], song_info[4][1:])

        result.append([song_info[1], song_info[2], m4aUrl, song_info[3], cover_url])
    logger.debug(f"{[result]}")
    return result

async def search_song_by_name(songName):
    matched = await get_song_mid(songName)
    return (await handle_informations(matched))

if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete((search_song_by_name("Igallta")))
