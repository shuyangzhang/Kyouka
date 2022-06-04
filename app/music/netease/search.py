import aiohttp


NETEASE_API = "http://cloud-music.pl-fe.cn/"
NETEASE_SOURCE_URL = "http://music.163.com/song/media/outer/url"

async def fetch_music_source_by_name(music_name: str):
    url = f"{NETEASE_API}search?keywords={music_name}&limit=1&offset=0&type=1"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            resp_json = await r.json()
            status = resp_json.get("code", 500)
            if status == 500:
                raise Exception(resp_json.get("error", "fetch music source failed, unknown reason."))
            else:
                data = resp_json.get("result", {}).get("songs", [])
                if data:
                    matched = True
                    name = data[0].get("name", music_name)
                    artists = data[0].get("artists", [])
                    if not artists:
                        vocalist = "未知歌手"
                    else:
                        vocalist = artists[0].get("name", "未知歌手")
                    music_id = data[0].get("id")
                    source = f"{NETEASE_SOURCE_URL}?id={music_id}.mp3"
                    duration = data[0].get("duration", 180000)
                else:
                    matched = False
                    name = ""
                    vocalist = ""
                    source = ""
                    duration = 0

    print(matched, name, vocalist, source, duration)
    return matched, name, vocalist, source, duration

async def search_music_by_keyword(music_name: str, limit: int=5):
    url = f"{NETEASE_API}search?keywords={music_name}&limit={limit}&offset=0&type=1"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            resp_json = await r.json()
            status = resp_json.get("code", 500)
            if status != 200:
                raise Exception(resp_json.get("error", "fetch music source failed, unknown reason."))
            else:
                data = resp_json.get("result", {}).get("songs", [])
                if data:
                    matched = True
                    candidates = []

                    for this_music in data:
                        name = this_music.get("name")
                        artists = this_music.get("artists", [])
                        if not artists:
                            vocalist = "未知歌手"
                        else:
                            vocalist = artists[0].get("name", "未知歌手")
                        music_id = this_music.get("id")
                        source = f"{NETEASE_SOURCE_URL}?id={music_id}.mp3"
                        duration = this_music.get("duration", 180000)

                        candidates.append([name, vocalist, source, duration])                        
                else:
                    matched = False
                    candidates = []

    print(candidates)
    return matched, candidates


if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(search_music_by_keyword("篇章"))
