import datetime

from loguru import logger
from khl import Message, Bot
from khl.card import CardMessage
from app.config.common import settings
from app.music.netease.search import fetch_music_source_by_name, search_music_by_keyword
from app.music.netease.playlist import fetch_music_list_by_id
from app.music.bilibili.search import bvid_to_music_by_bproxy
from app.voice_utils.container_handler import create_container, stop_container, pause_container, unpause_container
from app.utils.channel_utils import get_joined_voice_channel_id
from app.utils.log_utils import loguru_decorator as log
from app.task.interval_tasks import update_played_time_and_change_music, clear_expired_candidates_cache, keep_bproxy_alive

import app.CardStorage as CS


__version__ = "0.4.2"

# logger
if settings.file_logger:
    logger.add(f"{settings.container_name}.log", rotation="1 week")

bot = Bot(token=settings.token)


@bot.command(name="ping")
@log
async def ping(msg: Message):
    await msg.channel.send("コスモブルーフラッシュ！")
    logger.success(f"log_id: {msg.ctx.log_id} recieved")

@bot.command(name="version")
@log
async def version(msg: Message):
    await msg.channel.send(f"Version number: {__version__}")

@bot.command(name="help", aliases=["帮助", "文档", "手册", "说明", "示例", "命令", "?", "？"])
@log
async def help(msg: Message):
    await msg.channel.send(CardMessage(CS.HelpCard()))

@bot.command(name="debug")
@log
async def debug(msg: Message):
    if msg.author.id in settings.admin_users:
        settings.debug = not settings.debug
        if settings.debug:
            await msg.channel.send("debug switch is on")
        else:
            await msg.channel.send("debug switch is off")
    else:
        await msg.channel.send("permission denied")

@bot.command(name="channel", aliases=["频道", "语音频道"])
@log
async def update_voice_channel(msg: Message, channel_id: str=""):
    if not channel_id:
        raise Exception("输入格式有误。\n正确格式为: /channel {channel_id} 或 /频道 {channel_id}")
    else:
        settings.channel = channel_id
        await msg.channel.send(f"语音频道更新为: {settings.channel}")

@bot.command(name="comehere", aliases=["来", "来我频道", "come"])
@log
async def come_to_my_voice_channel(msg: Message):
    guild_id = msg.ctx.guild.id
    author_id = msg.author.id

    author_voice_channel_id = await get_joined_voice_channel_id(bot=bot, guild_id=guild_id, user_id=author_id)
    
    if author_voice_channel_id:
        await msg.channel.send(f"你当前所处的语音频道id为: {author_voice_channel_id}")
    else:
        raise Exception(f"请先进入一个语音频道后, 再使用这个命令")

    await bot.command.get("channel").handler(msg, author_voice_channel_id)

@bot.command(name="play", aliases=["点歌"])
@log
async def play_music(msg: Message, *args):
    music_name = " ".join(args)
    if not music_name:
        raise Exception("输入格式有误。\n正确格式为: /play {music_name} 或 /点歌 {music_name}")
    else:
        matched, name, vocalist, source, duration, cover_image_url = await fetch_music_source_by_name(music_name)
        if matched:
            await msg.channel.send(f"已将 {name}-{vocalist} 添加到播放列表")
            settings.playqueue.append([name, vocalist, source, duration, -1, cover_image_url])
        else:
            await msg.channel.send(f"没有搜索到歌曲: {music_name} 哦，试试搜索其他歌曲吧")

@bot.command(name='import', aliases=["导入", "导入歌单"])
@log
async def import_music_by_playlist(msg: Message, playlist_id : str=""):
    if not playlist_id:
        raise Exception("输入格式有误。\n正确格式为: /import {playlist_id} 或 /导入 {playlist_name}")
    else:
        result = await fetch_music_list_by_id(playlist_id=playlist_id)
        if not result:
            raise Exception("歌单为空哦，请检查你的输入")
        else:
            for this_music in result:
                settings.playqueue.append(this_music)
    await msg.channel.send("导入成功, 输入 /list 查看播放列表")
   
@bot.command(name="bilibili", aliases=["bili", "bzhan", "bv", "bvid", "b站", "哔哩哔哩", "叔叔"])
@log
async def play_audio_from_bilibili_video(msg: Message, BVid: str=""):
    if not BVid:
        raise Exception("输入格式有误。\n正确格式为: /bilibili {BVid} 或 /bv {BVid}")
    else:
        matched, name, author, source, duration, cover_image_url = await bvid_to_music_by_bproxy(BVid=BVid)
        if matched:
            await msg.channel.send(f"已将 {name}-{author} 添加到播放列表")
            settings.playqueue.append([name, author, source, duration, -1, cover_image_url])
        else:
            await msg.channel.send(f"没有搜索到对应的视频, 或音源无法抽提")

@bot.command(name="search", aliases=["搜索", "搜"])
@log
async def search_music(msg: Message, *args):
    keyword = " ".join(args)
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
            settings.candidates_map.pop(author_id, None)
            settings.candidates_map[author_id] = candidates_body

            # then generate the select menu
            select_menu_msg = "已匹配到如下结果：\n"
            for index, this_item in enumerate(candidates):
                this_item_str = f"<{index + 1}> {this_item[0]} - {this_item[1]} \n"
                select_menu_msg += this_item_str
            select_menu_msg += "\n输入 /select {编号} 或 /选 {编号} 即可加入歌单(一分钟内操作有效)"
            await msg.channel.send(select_menu_msg)

        else:
            await msg.channel.send(f"没有任何与关键词: {keyword} 匹配的信息, 试试搜索其他关键字吧")

@bot.command(name="select", aliases=["pick", "选择", "选"])
@log
async def select_candidate(msg: Message, candidate_num: str=""):
    candidate_num = int(candidate_num)
    if not candidate_num:
        raise Exception("输入格式有误。\n正确格式为: /select {编号} 或 /选 {编号}")
    else:
        author_id = msg.author.id
        if author_id not in settings.candidates_map:
            raise Exception("你还没有搜索哦, 或者是你的搜索结果已过期(1分钟)")
        else:
            candidates = settings.candidates_map[author_id].get("candidates")
            length = len(candidates)
            if candidate_num <= 0:
                raise Exception("输入不合法, 请不要输入0或者负数")
            elif candidate_num > length:
                raise Exception(f"搜索列表只有 {length} 个结果哦, 你不能选择第 {candidate_num} 个结果")
            else:
                selected_music = candidates[candidate_num - 1]
                settings.candidates_map.pop(author_id, None)
                settings.playqueue.append(selected_music)
                await msg.channel.send(f"已将 {selected_music[0]}-{selected_music[1]} 添加到播放列表")

@bot.command(name="list", aliases=["ls", "列表", "播放列表", "队列"])
@log
async def play_list(msg: Message):
    play_list = list(settings.playqueue)
    if not play_list:
        await msg.channel.send("当前的播放列表为空哦")
    else:
        from khl.requester import HTTPRequester
        # try card msg first, if it failed, then use cli msg
        try:
            await msg.reply(CardMessage(*CS.MusicListCard(play_list)))
        except HTTPRequester.APIRequestFailed:
            resp = ""
            for index, this_music in enumerate(play_list):
                resp += f"[{index + 1}] {this_music[0]} - {this_music[1]}"
                if index == 0:
                    resp += " <-- 正在播放 -->\n"
                else:
                    resp += "\n"
            await msg.channel.send(resp)
        except Exception as e:
            raise e
    
@bot.command(name="cut", aliases=["next", "切歌", "下一首", "切"])
@log
async def cut_music(msg: Message):
    play_list = list(settings.playqueue)
    if not play_list:
        await msg.channel.send("当前的播放列表为空哦")
    else:
        if len(play_list) == 1:
            await msg.channel.send("正在切歌，请稍候")
            settings.playqueue.popleft()
            await stop_container(settings.container_name)
            await msg.channel.send("后面没歌了哦")
            settings.played = 0
        else:
            await msg.channel.send("正在切歌，请稍候")
            settings.playqueue.popleft()
            await stop_container(settings.container_name)
            next_music = list(settings.playqueue)[0]
            await stop_container(settings.container_name)
            await create_container(settings.token, settings.channel, next_music[2], "false", settings.container_name)

            current_music = settings.playqueue.popleft()
            current_music[-2] = int(datetime.datetime.now().timestamp() * 1000) + current_music[3]
            settings.playqueue.appendleft(current_music)

            await msg.channel.send(f"正在为您播放 {next_music[0]} - {next_music[1]}")
            settings.played = 5000

@bot.command(name="remove", aliases=["rm", "删除", "删"])
@log
async def remove_music_in_play_list(msg: Message, music_number: str=""):
    music_number = int(music_number)
    if not music_number:
        raise Exception("格式输入有误。\n正确格式为: /remove {list_number} 或 /删除 {list_number}")
    else:
        play_list_length = len(settings.playqueue)
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
                play_list = list(settings.playqueue)
                removed_music = play_list[music_number - 1]
                del settings.playqueue[music_number - 1]
                await msg.channel.send(f"已将歌曲 {removed_music[0]}-{removed_music[1]} 从播放列表移除")

@bot.command(name="top", aliases=["置顶", "顶"])
@log
async def make_music_at_top_of_play_list(msg: Message, music_number: str=""):
    music_number = int(music_number)
    if not music_number:
        raise Exception("格式输入有误。\n正确格式为: /top {list_number} 或 /顶 {list_number}")
    else:
        play_list_length = len(settings.playqueue)
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
                play_list = list(settings.playqueue)
                to_top_music = play_list[music_number - 1]
                del settings.playqueue[music_number - 1]
                settings.playqueue.insert(1, to_top_music)
                await msg.channel.send(f"已将歌曲 {to_top_music[0]}-{to_top_music[1]} 在播放列表中置顶")

@bot.command(name="pause", aliases=["暂停"])
@log
async def pause(msg: Message):
    await pause_container(settings.container_name)

@bot.command(name="unpause", aliases=["取消暂停", "继续"])
@log
async def unpause(msg: Message):
    await unpause_container(settings.container_name)

"""
@bot.command(name="stop", aliases=["停止", "结束"])
async def stop_music(msg: Message):
    await msg.channel.send("正在结束...请稍候")
    await stop_container(settings.container_name)
"""

@bot.command(name="logout")
@log
async def logout(msg: Message):
    if msg.author.id in settings.admin_users:
        await msg.channel.send("logging out now...")
        raise KeyboardInterrupt()
    else:
        await msg.channel.send("permission denied")


# repeated tasks
@bot.task.add_interval(seconds=5)
async def five_seconds_interval_tasks():
    await update_played_time_and_change_music()

@bot.task.add_interval(seconds=10)
async def ten_seconds_interval_tasks():
    await clear_expired_candidates_cache()

@bot.task.add_interval(minutes=1)
async def one_minutes_interval_tasks():
    await keep_bproxy_alive()


# buttons reflection event, WIP
from khl import Event,EventTypes
@bot.on_event(EventTypes.MESSAGE_BTN_CLICK)
async def msg_btn_click(b:Bot,event:Event):
    channel = await b.fetch_public_channel(event.body['target_id'])
    value = event.body['value']
    action, *args = (value.split(":"))
    await channel.send(f"action:{action} arg:{args}")
    # use action to do something
    
    # this function is WIP 
##################


###################
# I personally think the following features (personalized regular matching commands, contributed by Froyo) 
# are suitable for a private bot, not for an open source release, I've commented this part out for now, 
# if I have better thoughts and ideas I'll restore these features.
#                                                                        -- manako. 11th, June, 2022.
###################

'''
######################
## re command support

# 正则处理时是否开启前缀
RE_PREFIX_ENABLE = True

# 正则前缀是否必须位于 最开始
RE_PREFIX_INBEGINN = True

# 正则处理时的命令前缀
RE_PREFIX = (r"^" if RE_PREFIX_ENABLE else r"") + (r"(?:[kK][yY][Oo][Uu][Kk][Aa]|[kK]{2}).*?" if RE_PREFIX_ENABLE else r"")

######################

######################
## 正则的语义交流转换
@bot.command(name="RE_play_music",regex= RE_PREFIX + r'(?:来首|点歌|来一首|点首|点一首)[ ]?(.*)')
async def regular_play_music(msg:Message, music_name:str):
    """
    点歌，加入列表
    :param music_name: 歌曲名，通过正则获取
    :other: 此处唤醒示例为: Kyouka来首STAY / kyouka 播放 STAY / kyouka 我要点歌 STAY / ... 
    """
    if settings.re_prefix_switch:
        await bot.command.get("play").handler(msg, music_name)
    
# 列表 这里有更好的唤醒方法可以再提
@bot.command(name="RE_list_music",regex= RE_PREFIX + r'(?:列表|播放列表|队列).*?')
async def regular_list_music(msg:Message):
    """
    print music list
    """
    if settings.re_prefix_switch:
        await bot.command.get("list").handler(msg)
    
# 来我房间
@bot.command(name="RE_come_here",regex= RE_PREFIX + r'来我(?:房间|频道|语音).*?')
async def regular_come_here(msg:Message):
    if settings.re_prefix_switch:
        await bot.command.get("comehere").handler(msg)

# 下一首歌
@bot.command(name="RE_cut_music",regex= RE_PREFIX + r'(?:切歌|换歌|下一首|切).*?')
async def regular_cut_music(msg:Message):
    """
    next music(regular)
    """
    if settings.re_prefix_switch:
        await bot.command.get("cut").handler(msg)

#########################
'''
