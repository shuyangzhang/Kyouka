from khl import Bot, Message
from khl.card import CardMessage

async def update_cardmessage_by_message(msg: Message, msg_id, content):
    method = 'POST'
    route = 'message/update'
    json = {
        'msg_id': msg_id,
        'content': content
    }
    await msg.ctx.gate.request(method=method, route=route, json=json)

async def update_cardmessage_by_bot(bot: Bot, msg_id: str, content: CardMessage):
    method = 'POST'
    route = 'message/update'
    json = {
        'msg_id': msg_id,
        'content': content
    }
    await bot.client.gate.request(method=method, route=route, json=json)