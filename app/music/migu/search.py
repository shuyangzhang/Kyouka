import os
import aiohttp
from mutagen.mp3 import MP3

from app.music.music import Music

USER_AGENT = "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1"
MIGU_API = 'https://m.music.migu.cn/migu/remoting/scr_search_tag'

CACHE_PATH = os.path.join(os.path.dirname(__file__), 'cache')

async def msearch_music_by_keyword(music_name: str, limit: int=5) -> list[Music]:

    headers = {
        "referer": "https://m.music.migu.cn/v3",
        "User-Agent": USER_AGENT
    }

    params = {
        'rows': 20,
        'type': 2,
        'pgc': 1,
        'keyword': music_name
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(MIGU_API, headers=headers, params=params) as req:
            if req.status != 200:
                raise Exception('get migu api failed')

            resp_json = await req.json()
            candidates = []

            if resp_json['success']:
                
                musiclist = resp_json.get('musics', [])

                while musiclist and len(candidates) <= limit:
                    music: dict = musiclist.pop(0)
                    name = music.get('songName', '未知')
                    artist = music.get('artist', '未知歌手')
                    cover_image_url = music.get('cover', '')
                    if music['mp3']:
                        source = music.get('mp3', '')
                        temp_file_path = await get_mp3_file(source, music['id'])
                        audio = MP3(temp_file_path)
                        duration = round(audio.info.length * 1000)
                        os.remove(temp_file_path)
                        
                        candidates.append(Music(name, artist, source, duration, cover_image_url))
            
    return candidates


async def get_mp3_file(url: str, name: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as req:
            temp_file_path = os.path.join(CACHE_PATH, f'{name}.mp3')
            with open(temp_file_path, 'wb') as f:
                f.write(await req.read())

    return temp_file_path


if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(msearch_music_by_keyword('两人雨天'))
    