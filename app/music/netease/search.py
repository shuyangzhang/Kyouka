import aiohttp
import json


QQWTT_SEARCH_API = "https://www.qqwtt.com/"

async def fetch_music_source_by_name(music_name: str):
    headers = {
        "x-requested-with": "XMLHttpRequest"
    }
    form = aiohttp.FormData()
    form.add_field("input", music_name)
    form.add_field("filter", "name")
    form.add_field("type", "netease")
    form.add_field("page", 1)

    async with aiohttp.ClientSession() as session:
        async with session.post(QQWTT_SEARCH_API, headers=headers, data=form) as response:
            resp = await response.text()
            resp_json = json.loads(resp)
            status = resp_json.get("code", 500)
            if status == 500:
                raise Exception(resp_json.get("error", "fetch music source failed, unknown reason."))
            else:
                data = resp_json.get("data", [])
                if data:
                    matched = True
                    name = data[0].get("title", music_name)
                    vocalist = data[0].get("author", "未知歌手")
                    source = data[0].get("url")
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
