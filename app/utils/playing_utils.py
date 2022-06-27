from khl import Bot, Message
from app.config.common import settings


BUSY_STATUS_GAME_ID = 407348
FREE_STATUS_GAME_ID = 407350


async def set_playing_game_status_by_bot(bot: Bot, game_id: int):
    method = "POST"
    route = "game/activity"
    json = {
        "id": game_id,
        "data_type": 1,
    }
    resp_data = await bot.client.gate.request(method=method, route=route, json=json)

async def set_playing_game_status_by_message(msg: Message, game_id: int):
    method = "POST"
    route = "game/activity"
    json = {
        "id": game_id,
        "data_type": 1,
    }
    resp_data = await msg.ctx.gate.request(method=method, route=route, json=json)
