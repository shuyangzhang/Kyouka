from khl import Message, Bot
from dotenv import load_dotenv

import os
import traceback


__version__ = "0.1.0"

load_dotenv()

TOKEN= os.environ.get("TOKEN")
MUSIC_CHANNEL = os.environ.get("CHANNEL")
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

@bot.command(name="play", aliases=["点歌"])
async def play_music(msg: Message, music_name: str):
    try:
        pass
    except:
        if DEBUG:
            await msg.channel.send(traceback.format_exc())

@bot.command(name="pause", aliases=["暂停"])
async def pause(msg: Message):
    try:
        pass
    except:
        if DEBUG:
            await msg.channel.send(traceback.format_exc())

@bot.command(name="unpause", aliases=["取消暂停", "继续"])
async def unpause(msg: Message):
    try:
        pass
    except:
        if DEBUG:
            await msg.channel.send(traceback.format_exc())

@bot.command(name="logout")
async def logout(msg: Message):
    if msg.author.id in ["693543263"]:
        await msg.channel.send("logging out now...")
        raise KeyboardInterrupt()
    else:
        await msg.channel.send("permission denied")

