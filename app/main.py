import os
import traceback
import collections
import datetime

from khl import Message, Bot
from dotenv import load_dotenv
from app.music.netease.search import fetch_music_source_by_name, search_music_by_keyword
from app.voice_utils.container_handler import create_container, stop_container, pause_container, unpause_container
from app.utils.channel_utils import get_joined_voice_channel_id


__version__ = "0.3.0"

load_dotenv()

TOKEN= os.environ.get("TOKEN")
CHANNEL = os.environ.get("CHANNEL")
CONTAINER_NAME = os.environ.get("CONTAINER_NAME", "Kyouka")
RE_PREFIX_SWITCH = os.environ.get("RE_PREFIX_SWITCH", False)

DEBUG = False

PLAYED = 0  # ms
PLAYQUEUE = collections.deque()
LOCK = False

CANDIDATES_MAP = {}
CANDIDATES_LOCK = False

######################
## re command support

# 正则处理时是否开启前缀
RE_PREFIX_ENABLE = True

# 正则前缀是否必须位于 最开始
RE_PREFIX_INBEGINN = True

# 正则处理时的命令前缀
RE_PREFIX = (r"^" if RE_PREFIX_ENABLE else r"") + (r"(?:[kK][yY][Oo][Uu][Kk][Aa]|[kK]{2}).*?" if RE_PREFIX_ENABLE else r"")

######################

bot = Bot(token=TOKEN)


################## music
from khl import Event,EventTypes
@bot.on_event(EventTypes.MESSAGE_BTN_CLICK)
async def msg_btn_click(b:Bot,event:Event):
    channel = await b.fetch_public_channel(event.body['target_id'])
    value = event.body['value']
    action, *args = (value.split(":"))
    await channel.send(f"action:{action} arg:{args}")
    # use action to do something

##################


######################
## 正则的语义交流转换
@bot.command(name="RE_play_music",regex= RE_PREFIX + r'(?:来首|点歌|来一首|点首|点一首)[ ]?(.*)')
async def regular_play_music(msg:Message, music_name:str):
    """
    点歌，加入列表
    :param music_name: 歌曲名，通过正则获取
    :other: 此处唤醒示例为: Kyouka来首STAY / kyouka 播放 STAY / kyouka 我要点歌 STAY / ... 
    """
    if RE_PREFIX_SWITCH:
        await bot.command.get("play").handler(msg, music_name)
    
# 列表 这里有更好的唤醒方法可以再提
@bot.command(name="RE_list_music",regex= RE_PREFIX + r'(?:列表|播放列表|队列).*?')
async def regular_list_music(msg:Message):
    """
    print music list
    """
    if RE_PREFIX_SWITCH:
        await bot.command.get("list").handler(msg)
    
# 来我房间
@bot.command(name="RE_come_here",regex= RE_PREFIX + r'来我(?:房间|频道|语音).*?')
async def regular_come_here(msg:Message):
    if RE_PREFIX_SWITCH:
        await bot.command.get("comehere").handler(msg)

# 下一首歌
@bot.command(name="RE_cut_music",regex= RE_PREFIX + r'(?:切歌|换歌|下一首|切).*?')
async def regular_cut_music(msg:Message):
    """
    next music(regular)
    """
    if RE_PREFIX_SWITCH:
        await bot.command.get("cut").handler(msg)

#########################

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

@bot.command(name="comehere", aliases=["来", "来我频道", "come"])
async def come_to_my_voice_channel(msg: Message):
    try:
        guild_id = msg.ctx.guild.id
        author_id = msg.author.id

        author_voice_channel_id = await get_joined_voice_channel_id(bot=bot, guild_id=guild_id, user_id=author_id)
        
        if author_voice_channel_id:
            await msg.channel.send(f"你当前所处的语音频道id为: {author_voice_channel_id}")
        else:
            raise Exception(f"请先进入一个语音频道后, 再使用这个命令")

        await bot.command.get("channel").handler(msg, author_voice_channel_id)

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
                PLAYQUEUE.append([name, vocalist, source, duration])
            else:
                await msg.channel.send(f"没有搜索到歌曲: {music_name} 哦，试试搜索其他歌曲吧")
    except Exception as e:
        if DEBUG:
            await msg.channel.send(traceback.format_exc())
        else:
            await msg.channel.send(str(e))

@bot.command(name="search", aliases=["搜索", "搜"])
async def search_music(msg: Message, keyword: str=""):
    global CANDIDATES_MAP

    try:
        if not keyword:
            raise Exception("输入格式有误。\n正确格式为: /search {keyword} 或 /搜 {keyword}")
        else:
            matched, candidates = await search_music_by_keyword(music_name=keyword)
            if matched:
                # put candidates into global cache first
                author_id = msg.author.id
                expire = datetime.datetime.now() + datetime.timedelta(minutes=1)
                candidates_body = {
                    "candidates": candidates,
                    "expire": expire,
                }
                CANDIDATES_MAP.pop(author_id, None)
                CANDIDATES_MAP[author_id] = candidates_body

                # then generate the select menu
                select_menu_msg = "已匹配到如下结果：\n"
                for index, this_item in enumerate(candidates):
                    this_item_str = f"<{index + 1}> {this_item[0]} - {this_item[1]} \n"
                    select_menu_msg += this_item_str
                select_menu_msg += "\n输入 /select {编号} 或 /选 {编号} 即可加入歌单(一分钟内操作有效)"
                await msg.channel.send(select_menu_msg)

            else:
                await msg.channel.send(f"没有任何与关键词: {keyword} 匹配的信息, 试试搜索其他关键字吧")
    except Exception as e:
        if DEBUG:
            await msg.channel.send(traceback.format_exc())
        else:
            await msg.channel.send(str(e))

@bot.command(name="select", aliases=["pick", "选择", "选"])
async def select_candidate(msg: Message, candidate_num: int=0):
    global CANDIDATES_MAP
    global PLAYQUEUE

    try:
        if not candidate_num:
            raise Exception("输入格式有误。\n正确格式为: /select {编号} 或 /选 {编号}")
        else:
            author_id = msg.author.id
            if author_id not in CANDIDATES_MAP:
                raise Exception("你还没有搜索哦, 或者是你的搜索结果已过期(1分钟)")
            else:
                candidates = CANDIDATES_MAP[author_id].get("candidates")
                length = len(candidates)
                if candidate_num <= 0:
                    raise Exception("输入不合法, 请不要输入0或者负数")
                elif candidate_num > length:
                    raise Exception(f"搜索列表只有 {length} 个结果哦, 你不能选择第 {candidate_num} 个结果")
                else:
                    selected_music = candidates[candidate_num - 1]
                    CANDIDATES_MAP.pop(author_id, None)
                    PLAYQUEUE.append(selected_music)
                    await msg.channel.send(f"已将 {selected_music[0]}-{selected_music[1]} 添加到播放列表")

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
                await stop_container(CONTAINER_NAME)
                await msg.channel.send("后面没歌了哦")
                PLAYED = 0
            else:
                await msg.channel.send("正在切歌，请稍候")
                PLAYQUEUE.popleft()
                await stop_container(CONTAINER_NAME)
                next_music = list(PLAYQUEUE)[0]
                await stop_container(CONTAINER_NAME)
                await create_container(TOKEN, CHANNEL, next_music[2], "false", CONTAINER_NAME)
                await msg.channel.send(f"正在为您播放 {next_music[0]} - {next_music[1]}")
                PLAYED = 5000
    except Exception as e:
        if DEBUG:
            await msg.channel.send(traceback.format_exc())
        else:
            await msg.channel.send(str(e))

@bot.command(name="remove", aliases=["rm", "删除", "删"])
async def remove_music_in_play_list(msg: Message, music_number: int=0):
    global PLAYQUEUE

    try:
        if not music_number:
            raise Exception("格式输入有误。\n正确格式为: /remove {list_number} 或 /删除 {list_number}")
        else:
            play_list_length = len(PLAYQUEUE)
            if not play_list_length:
                raise Exception("播放列表中没有任何歌曲哦")
            else:
                if music_number == 1:
                    raise Exception("不能删除正在播放的音乐, 请使用 /cut 直接切歌")
                elif music_number > play_list_length:
                    raise Exception(f"列表中一共只有 {play_list_length} 首歌, 你不能删除第 {music_number} 首歌")
                elif music_number <= 0:
                    raise Exception(f"输入不合法, 请不要输入0或者负数")
                else:
                    play_list = list(PLAYQUEUE)
                    removed_music = play_list[music_number - 1]
                    del PLAYQUEUE[music_number - 1]
                    await msg.channel.send(f"已将歌曲 {removed_music[0]}-{removed_music[1]} 从播放列表移除")

    except Exception as e:
        if DEBUG:
            await msg.channel.send(traceback.format_exc())
        else:
            await msg.channel.send(str(e))

@bot.command(name="top", aliases=["置顶", "顶"])
async def make_music_at_top_of_play_list(msg: Message, music_number: int=0):
    try:
        if not music_number:
            raise Exception("格式输入有误。\n正确格式为: /top {list_number} 或 /顶 {list_number}")
        else:
            play_list_length = len(PLAYQUEUE)
            if not play_list_length:
                raise Exception("播放列表中没有任何歌曲哦")
            else:
                if music_number == 1:
                    raise Exception("不能置顶正在播放的音乐, 它不是已经在播放了吗?")
                elif music_number > play_list_length:
                    raise Exception(f"列表中一共只有 {play_list_length} 首歌, 你置顶第 {music_number} 首歌")
                elif music_number <= 0:
                    raise Exception(f"输入不合法, 请不要输入0或者负数")
                else:
                    play_list = list(PLAYQUEUE)
                    to_top_music = play_list[music_number - 1]
                    del PLAYQUEUE[music_number - 1]
                    PLAYQUEUE.insert(1, to_top_music)
                    await msg.channel.send(f"已将歌曲 {to_top_music[0]}-{to_top_music[1]} 在播放列表中置顶")

    except Exception as e:
        if DEBUG:
            await msg.channel.send(traceback.format_exc())
        else:
            await msg.channel.send(str(e))


@bot.command(name="pause", aliases=["暂停"])
async def pause(msg: Message):
    try:
        await pause_container(CONTAINER_NAME)
    except Exception as e:
        if DEBUG:
            await msg.channel.send(traceback.format_exc())
        else:
            await msg.channel.send(str(e))

@bot.command(name="unpause", aliases=["取消暂停", "继续"])
async def unpause(msg: Message):
    try:
        await unpause_container(CONTAINER_NAME)
    except Exception as e:
        if DEBUG:
            await msg.channel.send(traceback.format_exc())
        else:
            await msg.channel.send(str(e))

"""
@bot.command(name="stop", aliases=["停止", "结束"])
async def stop_music(msg: Message):
    try:
        await msg.channel.send("正在结束...请稍候")
        await stop_container(CONTAINER_NAME)
    except Exception as e:
        if DEBUG:
            await msg.channel.send(traceback.format_exc())
        else:
            await msg.channel.send(str(e))
"""

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
    # print("PLAYED = ", PLAYED)
    # print("Q = ", PLAYQUEUE)
    # print("LOCK = ", LOCK)

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
                    await stop_container(CONTAINER_NAME)
                    await create_container(TOKEN, CHANNEL, first_music[2], "false", CONTAINER_NAME)
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
                            await stop_container(CONTAINER_NAME)
                            PLAYED = 0
                            LOCK = False
                            return None
                        else:
                            next_music = list(PLAYQUEUE)[0]
                            await stop_container(CONTAINER_NAME)
                            await create_container(TOKEN, CHANNEL, next_music[2], "false", CONTAINER_NAME)
                            PLAYED = 5000
                            LOCK = False
                            return None
        except Exception as e:
            LOCK = False
            print("Exception = ", str(e))

@bot.task.add_interval(seconds=10)
async def clear_expired_candidates_cache():
    global CANDIDATES_MAP
    global CANDIDATES_LOCK

    if CANDIDATES_LOCK:
        return None
    else:
        CANDIDATES_LOCK = True
        try:
            now = datetime.datetime.now()

            need_to_clear = []
            for this_user in CANDIDATES_MAP:
                if now >= CANDIDATES_MAP.get(this_user, {}).get("expire", now):
                    need_to_clear.append(this_user)
            
            for user_need_to_clear in need_to_clear:
                CANDIDATES_MAP.pop(user_need_to_clear, None)
                print(f"cache of user: {user_need_to_clear} is removed")
            
            CANDIDATES_LOCK = False
            return None

        except Exception as e:
            CANDIDATES_LOCK = False
            print("Exception = ", str(e))

