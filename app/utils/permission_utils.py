from khl import Message
from app.config.common import settings


def warn_decorator(func):
    async def wrapped_function(msg: Message, *args, **kwargs):
        user_id = msg.author.id
        if user_id in settings.warned_user_list:
            await msg.channel.send(f"检测到您最近有恶意绑定语音频道,恶意切歌,恶意添加/删除歌曲的行为, 请文明使用, 否则将会被封禁")
        await func(msg, *args, **kwargs)
    return wrapped_function

def ban_decorator(func):
    async def wrapped_function(msg: Message, *args, **kwargs):
        user_id = msg.author.id
        if user_id in settings.banned_user_list:
            await msg.channel.send(f"检测到您最近有恶意绑定语音频道,恶意切歌,恶意添加/删除歌曲的行为, 已被封禁")
            await msg.channel.send(f"如有误封, 请前往 镜华Kyouka 官方服务器的 #举报申诉 频道进行申诉")
        else:
            await func(msg, *args, **kwargs)
    return wrapped_function
