import os
import traceback
import collections

from khl import Message, Bot
from dotenv import load_dotenv
from app.music.netease.search import fetch_music_source_by_name
from app.voice_utils.container_handler import create_container, stop_container, pause_container, unpause_container

__version__ = "0.2.0"

load_dotenv()

TOKEN= os.environ.get("TOKEN")
CHANNEL = os.environ.get("CHANNEL")
REPEAT = os.environ.get("REPEAT", "true")

DEBUG = False

PLAYED = 0  # ms
PLAYQUEUE = collections.deque()
LOCK = False


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

@bot.command(name="play", aliases=["点歌"])
async def play_music(msg: Message, *args):
    global PLAYQUEUE
    try:
        music_name = "".join(args)
        if not music_name:
            raise Exception("输入格式有误。\n正确格式为: /play {music_name} 或 /点歌 {music_name}")
        else:
            matched, name, vocalist, source, duration = await fetch_music_source_by_name(music_name)
            if matched:
                await msg.channel.send(f"已将 {name}-{vocalist} 添加到播放列表")
                # await stop_container()
                # await create_container(token=TOKEN, channel=CHANNEL, source=source, repeat="true")
                PLAYQUEUE.append([name, vocalist, source, duration])
            else:
                await msg.channel.send(f"没有搜索到歌曲: {music_name} 哦，试试搜索其他歌曲吧")
    except Exception as e:
        if DEBUG:
            await msg.channel.send(traceback.format_exc())
        else:
            await msg.channel.send(str(e))

@bot.command(name="list", aliases=["列表", "播放列表", "队列"])
async def play_list(msg: Message):
    try:
        play_list = list(PLAYQUEUE)
        if not play_list:
            await msg.channel.send("当前的播放列表为空哦")
        else:
            resp = ""
            for index, this_music in enumerate(play_list):
                resp += f"[{index + 1}] {this_music[0]} - {this_music[1]}"
                if index == 0:
                    resp += " <-- 正在播放 -->\n"
                else:
                    resp += "\n"
            await msg.channel.send(resp)
    except Exception as e:
        if DEBUG:
            await msg.channel.send(traceback.format_exc())
        else:
            await msg.channel.send(str(e))
    
@bot.command(name="cut", aliases=["next", "切歌", "下一首", "切"])
async def cut_music(msg: Message):
    global PLAYQUEUE
    global PLAYED

    try:
        play_list = list(PLAYQUEUE)
        if not play_list:
            await msg.channel.send("当前的播放列表为空哦")
        else:
            if len(play_list) == 1:
                await msg.channel.send("正在切歌，请稍候")
                PLAYQUEUE.popleft()
                await stop_container()
                await msg.channel.send("后面没歌了哦")
                PLAYED = 0
            else:
                await msg.channel.send("正在切歌，请稍候")
                PLAYQUEUE.popleft()
                await stop_container()
                next_music = list(PLAYQUEUE)[0]
                await stop_container()
                await create_container(TOKEN, CHANNEL, next_music[2], "false")
                await msg.channel.send(f"正在为您播放 {next_music[0]} - {next_music[1]}")
                PLAYED = 5000
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

# repeated tasks
@bot.task.add_interval(seconds=5)
async def update_played_time_and_change_music():
    global PLAYED
    global PLAYQUEUE
    global LOCK
    print("PLAYED = ", PLAYED)
    print("Q = ", PLAYQUEUE)
    print("LOCK = ", LOCK)

    if LOCK:
        return None
    else:
        LOCK = True

        try:
            if len(PLAYQUEUE) == 0:
                PLAYED = 0
                LOCK = False
                return None
            else:
                first_music = list(PLAYQUEUE)[0]
                if PLAYED == 0:
                    await stop_container()
                    await create_container(TOKEN, CHANNEL, first_music[2], "false")
                    PLAYED += 5000
                    LOCK = False
                    return None
                else:
                    duration = first_music[3]
                    if PLAYED + 5000 < duration:
                        PLAYED += 5000
                        LOCK = False
                        return None
                    else:
                        PLAYQUEUE.popleft()
                        if len(PLAYQUEUE) == 0:
                            await stop_container()
                            PLAYED = 0
                            LOCK = False
                            return None
                        else:
                            next_music = list(PLAYQUEUE)[0]
                            await stop_container()
                            await create_container(TOKEN, CHANNEL, next_music[2], "false")
                            PLAYED = 5000
                            LOCK = False
                            return None
        except Exception as e:
            LOCK = False
            print("Exception = ", str(e))



