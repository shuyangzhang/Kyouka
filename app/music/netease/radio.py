import json
import re

import aiohttp
from loguru import logger

from app.music.netease.search import NETEASE_SOURCE_URL

NETEASE_RADIO_LIST_API = 'https://music.163.com/radio/'
NETEASE_PROGRAM_DETAIL_API = 'https://music.163.com/api/dj/program/detail'
NETEASE_PROGRAM_ID_PATTERN = re.compile(r'<a href="/program\?id=(\d+)".*?>.*?</a>')


async def fetch_program_details_by_id(program_id):
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
                    matched = True
                    name = song['name']
                    vocalist = song.get('artists', [{}])[0].get('name', '未知歌手')
                    song_id = song['id']
                    source = f'{NETEASE_SOURCE_URL}?id={song_id}.mp3'
                    duration = song.get("duration", 180000)
                    cover_image_url = program['coverUrl']
                    cover_image_url = f"{cover_image_url}?param=130y130" if cover_image_url else cover_image_url
                else:
                    matched = False
                    name = vocalist = source = cover_image_url = ""
                    duration = 0
    return matched, name, vocalist, source, duration, cover_image_url


async def fetch_program_ids_by_radio_id(radio_id: str):
    url = f"{NETEASE_RADIO_LIST_API}?id={radio_id}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            response = await r.text()
            matches = NETEASE_PROGRAM_ID_PATTERN.findall(response)
            if not matches:
                raise Exception(f'无法查询到电台：{radio_id} 中的节目，请检查你的输入')
            else:
                return matches
    return []


async def fetch_radio_by_id(radio_id: str):
    result = []
    program_ids = await fetch_program_ids_by_radio_id(radio_id)
    for prog_id in program_ids:
        matched, name, vocalist, source, duration, cover_image_url = await fetch_program_details_by_id(prog_id)
        if matched:
            result.append([name, vocalist, source, duration, -1, cover_image_url])

    logger.debug(f'{result}')
    return result
