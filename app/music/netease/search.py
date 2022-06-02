import aiohttp
import json


NETEASE_API = "http://cloud-music.pl-fe.cn/"
NETEASE_SOURCE_URL = "http://music.163.com/song/media/outer/url"

async def fetch_music_source_by_name(music_name: str):
    # headers = {
    #     "x-requested-with": "XMLHttpRequest"
    # }
    # form = aiohttp.FormData()
    # form.add_field("input", music_name)
    # form.add_field("filter", "name")
    # form.add_field("type", "netease")
    # form.add_field("page", 1)
    url = f"{NETEASE_API}search?keywords={music_name}&limit=1&offset=0&type=1"
    async with aiohttp.ClientSession() as session:
        # async with session.post(QQWTT_SEARCH_API, headers=headers, data=form) as response:
            # resp = await response.text()
            # resp_json = json.loads(resp)

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
                else:
                    matched = False
                    name = ""
                    vocalist = ""
                    source = ""

    print(matched, name, vocalist, source)
    return matched, name, vocalist, source


if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(fetch_music_source_by_name("篇章"))
