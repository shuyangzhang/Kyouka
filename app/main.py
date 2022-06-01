import os
import traceback

from khl import Message, Bot
from dotenv import load_dotenv
from app.music.netease.search import fetch_music_source_by_name
from app.voice_utils.container_handler import create_container, stop_container, pause_container, unpause_container

__version__ = "0.1.0"

load_dotenv()

TOKEN= os.environ.get("TOKEN")
CHANNEL = os.environ.get("CHANNEL")
REPEAT = os.environ.get("REPEAT", "true")

DEBUG = False

bot = Bot(token=TOKEN)

@bot.command(name="ping")
async def ping(msg: Message):
    await msg.channel.send("コスモブルーフラッシュ！")

@bot.command(name="version")
async def version(msg: Message):
    await msg.channel.send(f"Version number: {__version__}")

@bot.command(name="debug")
async def debug(msg: Message):
    if msg.author.id in ["693543263"]:
        global DEBUG
        DEBUG = not DEBUG
        if DEBUG:
            await msg.channel.send("debug switch is on")
        else:
            await msg.channel.send("debug switch is off")
    else:
        await msg.channel.send("permission denied")

@bot.command(name="channel", aliases=["频道", "语音频道"])
async def update_voice_channel(msg: Message, channel_id: str=""):
    try:
        if not channel_id:
            raise Exception("输入格式有误。\n正确格式为: /channel {channel_id} 或 /频道 {channel_id}")
        else:
            global CHANNEL
            CHANNEL = channel_id
            await msg.channel.send(f"语音频道更新为: {CHANNEL}")
    except Exception as e:
        if DEBUG:
            await msg.channel.send(traceback.format_exc())
        else:
            await msg.channel.send(str(e))

@bot.command(name="play", aliases=["点歌", "播放"])
async def play_music(msg: Message, music_name: str=""):
    try:
        if not music_name:
            raise Exception("输入格式有误。\n正确格式为: /play {music_name} 或 /点歌 {music_name}")
        else:
            matched, name, vocalist, source = await fetch_music_source_by_name(music_name)
            if matched:
                await msg.channel.send(f"正在为您播放 {name}-{vocalist}, 请稍等")
                await stop_container()
                await create_container(token=TOKEN, channel=CHANNEL, source=source, repeat="true")
    except Exception as e:
        if DEBUG:
            await msg.channel.send(traceback.format_exc())
        else:
            await msg.channel.send(str(e))

@bot.command(name="pause", aliases=["暂停"])
async def pause(msg: Message):
    try:
        await pause_container()
    except Exception as e:
        if DEBUG:
            await msg.channel.send(traceback.format_exc())
        else:
            await msg.channel.send(str(e))

@bot.command(name="unpause", aliases=["取消暂停", "继续"])
async def unpause(msg: Message):
    try:
        await unpause_container()
    except Exception as e:
        if DEBUG:
            await msg.channel.send(traceback.format_exc())
        else:
            await msg.channel.send(str(e))

@bot.command(name="stop", aliases=["停止", "结束"])
async def stop_music(msg: Message):
    try:
        await msg.channel.send("正在结束...请稍候")
        await stop_container()
    except Exception as e:
        if DEBUG:
            await msg.channel.send(traceback.format_exc())
        else:
            await msg.channel.send(str(e))

@bot.command(name="logout")
async def logout(msg: Message):
    if msg.author.id in ["693543263"]:
        await msg.channel.send("logging out now...")
        raise KeyboardInterrupt()
    else:
        await msg.channel.send("permission denied")

