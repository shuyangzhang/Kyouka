import re

import aiohttp
from loguru import logger

from app.music.music import Music
from app.music.netease.details import fetch_program_details_by_id

NETEASE_RADIO_LIST_API = 'https://music.163.com/radio/'
NETEASE_PROGRAM_ID_PATTERN = re.compile(r'<a href="/program\?id=(\d+)".*?>.*?</a>')


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


async def fetch_radio_by_id(radio_id: str) -> list[Music]:
    program_ids = await fetch_program_ids_by_radio_id(radio_id)
    result = [await fetch_program_details_by_id(prog_id) for prog_id in program_ids]

    logger.debug(f'{result}')
    return result
