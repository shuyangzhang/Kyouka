from khl import Bot, Message

async def update_cardmessage_by_message(msg: Message, msg_id: str, content: str):
    method = 'POST'
    route = 'message/update'
    json = {
        'msg_id': msg_id,
        'content': content
    }
    await msg.ctx.gate.request(method=method, route=route, json=json)

async def update_cardmessage_by_bot(bot: Bot, msg_id: str, content: str):
    method = 'POST'
    route = 'message/update'
    json = {
        'msg_id': msg_id,
        'content': content
    }
    await bot.client.gate.request(method=method, route=route, json=json)