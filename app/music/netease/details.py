import json
from typing import Optional

import aiohttp

from app.music.music import Music

NETEASE_DETAIL_URL = 'http://music.163.com/api/song/detail/'
NETEASE_SOURCE_URL = 'http://music.163.com/song/media/outer/url'
NETEASE_PROGRAM_DETAIL_API = 'https://music.163.com/api/dj/program/detail'


async def song_ids_to_instances(*song_ids: int) -> list[Music]:
    url = f'{NETEASE_DETAIL_URL}?ids=[{", ".join(map(str, song_ids))}]'

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            resp_json = json.loads(await r.text())  # response is not application/json
            status = resp_json.get('code', 500)
            if status != 200:
                raise Exception(resp_json.get('error', f'fetch music details failed, code is {status}.'))
            else:
                songs = resp_json.get('songs', [])
                return [Music(
                    song.get('name'),
                    song.get('artists', [{}])[0].get('name', '未知歌手'),
                    f'{NETEASE_SOURCE_URL}?id={song.get("id")}.mp3',
                    song.get('duration', 180000),
                    f'{song.get("album", {}).get("picUrl", "")}?param=130y130'
                ) for song in songs]


async def fetch_program_details_by_id(program_id) -> Optional[Music]:
    url = f'{NETEASE_PROGRAM_DETAIL_API}?id={program_id}'

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            resp_json = json.loads(await r.text())
            status = resp_json.get('code', 500)
            if status != 200:
                raise Exception(resp_json.get('error', 'fetch program details failed, unknown reason.'))
            else:
                program = resp_json.get('program', {})
                song = program.get('mainSong', {})
                if song:
                    return Music(
                        song['name'],
                        song.get('artists', [{}])[0].get('name', '未知歌手'),
                        f'{NETEASE_SOURCE_URL}?id={song["id"]}.mp3',
                        song.get('duration', 180000),
                        f'{program["coverUrl"]}?param=130y130'
                    )
    return None
