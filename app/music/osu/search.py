import aiohttp
import json
from loguru import logger

from app.music.music import Music

'''
osu!是一款免费的音乐游戏 →https://osu.ppy.sh/
osu!拥有在线排名，多人游戏模式以及自称50万活跃玩家的社区
xD
'''

SAYO_SEARCH_API = 'https://api.sayobot.cn/?post'
SAYO_MAPINFO_API = 'https://api.sayobot.cn/v2/beatmapinfo'

SAYO_THUMB = 'https://cdn.sayobot.cn:25225/beatmaps/{}/covers/cover.jpg'
SAYO_AUDIO = 'https://dl.sayobot.cn/beatmaps/files/{0}/{1}'


async def osearch_music_by_keyword(music_name: str) -> list[Music]:
    data = {
        'cmd': 'beatmaplist',
        'keyword': music_name,
        'type': 'search'
    }
    data = json.dumps(data)

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
        async with session.post(SAYO_SEARCH_API, data=data) as req:
            resp_json = await req.json()
            if req.status != 200:
                raise Exception('fetch music list failed, api is down')

            candidates = []
            if resp_json['status'] != -1:

                musiclist = resp_json.get('data', [])

                while musiclist and len(candidates) < 5:
                    music = musiclist.pop(0)
                    name = music['titleU'] if music['titleU'] else music['title']
                    artist = music['artistU'] if music['artistU'] else music['artist']
                    sid = music['sid']
                    match, duration, audio = await fetch_music_source_by_sid(sid)
                    if match:
                        if audio:
                            source = SAYO_AUDIO.format(sid, audio.replace(' ', '%20'))
                            cover_image_url = SAYO_THUMB.format(sid)
                            candidates.append(Music(name, artist, source, duration, cover_image_url))

    # logger.debug(f'{[str(music) for music in candidates]}')
    return candidates
                  
async def fetch_music_source_by_sid(sid: int):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
        async with session.get(SAYO_MAPINFO_API, params={'0': sid}) as req:
            # resp_json = await req.json()
            resp_json = json.loads(await req.text())
            if req.status != 200:
                return False, None, None

            if resp_json['status'] == -1:
                return False, None, None
            
            musicdata: dict = resp_json.get('data', {}).get('bid_data', [])[0]
            length = musicdata.get('length', 0)
            audio = musicdata.get('audio', '')
            return True, length, audio


if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(osearch_music_by_keyword('toaru shoukoku'))
