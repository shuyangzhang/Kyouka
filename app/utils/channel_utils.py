from typing import List
from khl import Bot 


async def get_joined_voice_channel_id(bot: Bot, guild_id: str, user_id: str) -> str: 
    method = "GET"
    route = "channel-user/get-joined-channel"
    resp_data = await bot.client.gate.request(method=method, route=f"{route}?guild_id={guild_id}&user_id={user_id}")
    items = resp_data.get("items", [])
    if items:
        channel_id = items[0].get("id", "")
    else:
        channel_id = ""
    return channel_id
