import re
import datetime
import json

from loguru import logger
from khl import Message, Bot, PublicMessage
from khl.card import CardMessage
from app.bot import bot
from app.config.common import settings
from app.music.netease.album import fetch_album_by_id
from app.music.netease.details import song_ids_to_instances
from app.music.netease.search import fetch_music_source_by_name, search_music_by_keyword
from app.music.netease.playlist import fetch_music_list_by_id
from app.music.netease.radio import fetch_radio_by_id
from app.music.bilibili.search import bvid_to_music_by_bproxy, bvid_to_music_by_local_bproxy
from app.music.osu.search import osearch_music_by_keyword
from app.music.qqmusic.search import qsearch_music_by_keyword
from app.music.migu.search import msearch_music_by_keyword
from app.voice_utils.container_async_handler import container_handler
from app.utils.channel_utils import get_joined_voice_channel_id
from app.utils.log_utils import loguru_decorator_factory as log
from app.utils.permission_utils import warn_decorator as warn
from app.utils.permission_utils import ban_decorator as ban
from app.utils.message_utils import update_cardmessage_by_bot
from app.task.interval_tasks import update_played_time_and_change_music, clear_expired_candidates_cache, keep_bproxy_alive, update_kanban_info, update_playing_game_status, keep_bot_market_heart_beat

import app.CardStorage as CS


__version__ = "0.8.0"

# logger
if settings.file_logger:
    logger.add(f"{settings.container_name}.log", rotation="1 week")

# bot = Bot(token=settings.token)
gate = bot.client.gate


@bot.command(name="ping")
@log(command="ping")
async def ping(msg: Message):
    await msg.channel.send("コスモブルーフラッシュ！")
    logger.success(f"log_id: {msg.ctx.log_id} recieved")


@bot.command(name="version")
@log(command="version")
async def version(msg: Message):
    await msg.channel.send(f"Version number: {__version__}")


@bot.command(name="help", aliases=["帮助", "文档", "手册", "说明", "示例", "命令", "?", "？"])
@log(command="help")
async def help(msg: Message):
    await msg.channel.send(CardMessage(CS.HelpCard()))


@bot.command(name="debug")
@log(command="debug")
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
@log(command="channel")
@ban
@warn
async def update_voice_channel(msg: Message, channel_id: str=""):
    if not channel_id:
        raise Exception("输入格式有误。\n正确格式为: /channel {channel_id} 或 /频道 {channel_id}")
    else:
        settings.channel = channel_id
        await msg.channel.send(f"语音频道更新为: {settings.channel}")


@bot.command(name="comehere", aliases=["来", "来我频道", "come"])
@log(command="comehere")
@ban
@warn
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
@log(command="play")
@ban
@warn
async def play_music(msg: Message, *args):
    music_name = " ".join(args)
    if not music_name:
        raise Exception("输入格式有误。\n正确格式为: /play {music_name} 或 /点歌 {music_name}")
    else:
        music = await fetch_music_source_by_name(music_name)
        if music:
            await msg.channel.send(CardMessage(CS.pickCard(music)))
            settings.playqueue.append(music)
        else:
            await msg.channel.send(f"没有搜索到歌曲: {music_name} 哦，试试搜索其他歌曲吧")


@bot.command(name="nid")
@log(command="nid")
@ban
@warn
async def play_music_using_netease_id(msg: Message, id: int):
    music = await song_ids_to_instances(id)
    if music:
        await msg.channel.send(CardMessage(CS.pickCard(music)))
        settings.playqueue.append(music)
    else:
        await msg.channel.send(f"没有找到 ID 为 {id} 的歌曲哦")


@bot.command(name='playlist', aliases=["歌单", "导入歌单"])
@log(command="playlist")
@ban
@warn
async def import_music_by_playlist(msg: Message, playlist_url : str=""):
    if not playlist_url:
        raise Exception("输入格式有误。\n正确格式为: /playlist {playlist_url} 或 /歌单 {playlist_url}")
    else:
        netease_playlist_pattern = re.compile(r"(?:playlist|^)(?:/|)(?:\?id=|)(\d+)")
        matched_obj = netease_playlist_pattern.search(playlist_url)
        if matched_obj:
            playlist_id = matched_obj.groups()[0]
        else:
            raise Exception("输入格式有误。\n正确格式为: /playlist {playlist_url} 或 /歌单 {playlist_url}")
        await msg.channel.send("正在逐条导入歌单音乐，请稍候")
        result = await fetch_music_list_by_id(playlist_id=playlist_id)
        if not result:
            raise Exception("歌单为空哦，请检查你的输入")
        else:
            if settings.public:
                settings.playqueue.extend(result[0:15])
            else:
                settings.playqueue.extend(result)
    await msg.channel.send("导入成功, 输入 /list 查看播放列表")


@bot.command(name='album', aliases=['专辑', '导入专辑'])
@log(command='album')
@ban
@warn
async def import_music_by_album(msg: Message, album_url: str=''):
    if not album_url:
        raise Exception('输入格式有误。\n正确格式为: /album {album_url} 或 /电台 {album_url}')
    else:
        netease_radio_pattern = re.compile(r'(?:album|^)(?:/|)(?:\?id=|)(\d+)')
        matched_obj = netease_radio_pattern.search(album_url)
        if matched_obj:
            album_id = matched_obj.groups()[0]
        else:
            raise Exception('输入格式有误。\n正确格式为: /album {album_url} 或 /电台 {album_url}')
        await msg.channel.send("正在逐条导入专辑音乐，请稍候")
        result = await fetch_album_by_id(album_id)
        if not result:
            raise Exception('专辑为空哦，请检查你的输入')
        else:
            if settings.public:
                settings.playqueue.extend(result[0:15])
            else:
                settings.playqueue.extend(result)
    await msg.channel.send('导入成功，输入 /list 查看播放列表')


@bot.command(name='radio', aliases=['djradio', '电台', '导入电台'])
@log(command='radio')
@ban
@warn
async def import_music_by_radio(msg: Message, radio_url: str = ''):
    if not radio_url:
        raise Exception('输入格式有误。\n正确格式为: /radio {radio_url} 或 /电台 {radio_url}')
    else:
        netease_radio_pattern = re.compile(r'(?:radio|^)(?:/|)(?:\?id=|)(\d+)')
        matched_obj = netease_radio_pattern.search(radio_url)
        if matched_obj:
            radio_id = matched_obj.groups()[0]
        else:
            raise Exception('输入格式有误。\n正确格式为: /radio {radio_url} 或 /电台 {radio_url}')
        await msg.channel.send("正在逐条导入电台节目，请稍候")
        result = await fetch_radio_by_id(radio_id=radio_id)
        if not result:
            raise Exception('电台为空哦，请检查你的输入')
        else:
            if settings.public:
                settings.playqueue.extend(result[0:15])
            else:
                settings.playqueue.extend(result)
    await msg.channel.send('导入成功，输入 /list 查看播放列表')


@bot.command(name="bilibili", aliases=["bili", "bzhan", "bv", "bvid", "b站", "哔哩哔哩", "叔叔"])
@log(command="bilibili")
@ban
@warn
async def play_audio_from_bilibili_video(msg: Message, bilibili_url: str=""):
    if not bilibili_url:
        raise Exception("输入格式有误。\n正确格式为: /bilibili {bilibili_url} 或 /bv {bilibili_url}")
    else:
        BVid_pattern = re.compile(r"BV\w{10}")
        matched_obj = BVid_pattern.search(bilibili_url)
        if matched_obj:
            BVid = matched_obj.group()
        else:
            raise Exception("输入格式有误。\n正确格式为: /bilibili {bilibili_url} 或 /bv {bilibili_url}")
        if settings.local_bproxy:
            result = await bvid_to_music_by_local_bproxy(BVid=BVid)
        else:
            result = await bvid_to_music_by_bproxy(BVid=BVid)
        if result:
            await msg.channel.send(f"已将 {result.name}-{result.author} 添加到播放列表")
            settings.playqueue.append(result)
        else:
            await msg.channel.send(f"没有搜索到对应的视频, 或音源无法抽提")


@bot.command(name="search", aliases=["搜索", "搜"])
@log(command="search")
@ban
@warn
async def search_music(msg: Message, *args):
    keyword = " ".join(args)
    if not keyword:
        raise Exception("输入格式有误。\n正确格式为: /search {keyword} 或 /搜 {keyword}")
    else:
        netease_candidates = await search_music_by_keyword(music_name=keyword)
        qqmusic_candidates = await qsearch_music_by_keyword(bot, keyword)
        migu_candidates = await msearch_music_by_keyword(keyword)

        candidates = netease_candidates + migu_candidates + qqmusic_candidates
        if candidates:
            # put candidates into global cache first
            author_id = msg.author.id
            expire = datetime.datetime.now() + datetime.timedelta(minutes=1)
            candidates_body = {
                "candidates": candidates,
                "expire": expire,
            }
            settings.candidates_map.pop(author_id, None)
            settings.candidates_map[author_id] = candidates_body

            select_menu_msg = CardMessage(
                *CS.searchCard(
                    {
                        "netease": netease_candidates,
                        "migu": migu_candidates,
                        "qqmusic": qqmusic_candidates
                    }
                )
            )
            from khl.requester import HTTPRequester
            try:
                await msg.reply(select_menu_msg)
                # await msg.reply(str(list(select_menu_msg)))
            except HTTPRequester.APIRequestFailed:
                # select_menu_msg = '已搜索到以下结果\n' + \
                #     '\n'.join(f"<{i + 1}> {candidate.name} - {candidate.author}" for i, candidate in enumerate(candidates)) + \
                #     '\n输入 /select {编号} 或 /选 {编号} 即可加入歌单(一分钟内操作有效)'
                # await msg.reply(select_menu_msg)
                await msg.reply(str(list(select_menu_msg)))
            except Exception as e:
                raise e

        else:
            await msg.reply(f"没有任何与关键词: {keyword} 匹配的信息, 试试搜索其他关键字吧")


@bot.command(name="nsearch", aliases=["wyy", "wyysearch", "搜索网易云", "搜网易"])
@log(command="nsearch")
@ban
@warn
async def search_netease(msg: Message, *args):
    keyword = " ".join(args)
    if not keyword:
        raise Exception("输入格式有误。\n正确格式为: /search {keyword} 或 /搜 {keyword}")
    else:
        candidates = await search_music_by_keyword(music_name=keyword)
        if candidates:
            # put candidates into global cache first
            author_id = msg.author.id
            expire = datetime.datetime.now() + datetime.timedelta(minutes=1)
            candidates_body = {
                "candidates": candidates,
                "expire": expire,
            }
            settings.candidates_map.pop(author_id, None)
            settings.candidates_map[author_id] = candidates_body

            select_menu_msg = CardMessage(*CS.searchCard({"netease": candidates}))
            await msg.reply(select_menu_msg)

        else:
            await msg.reply(f"没有任何与关键词: {keyword} 匹配的信息, 试试搜索其他关键字吧")


@bot.command(name='osearch', aliases=['osu', 'osusearch', 'searchosu', '搜索osu', '搜osu'])
@log(command="osearch")
@ban
@warn
async def search_osu(msg: Message, *args):
    keyword = ' '.join(args)
    if not keyword:
        raise Exception("格式输入有误。\n正确格式为: /osearch {keyword} 或 /搜osu {keyword}")
    else:
        candidates = await osearch_music_by_keyword(music_name=keyword)
        if candidates:
            author_id = msg.author.id
            expire = datetime.datetime.now() + datetime.timedelta(minutes=1)
            candidates_body = {
                "candidates": candidates,
                "expire": expire
            }
            settings.candidates_map.pop(author_id, None)
            settings.candidates_map[author_id] = candidates_body

            select_menu_msg = CardMessage(*CS.searchCard({"osu": candidates}))
            await msg.reply(select_menu_msg)

        else:
            await msg.reply(f"没有任何与关键词: {keyword} 匹配的信息, 试试搜索其他关键字吧")


@bot.command(name='msearch', aliases=['migu', 'migusearch', 'searchmigu', '搜索咪咕', '搜咪咕', '咪咕音乐'])
@log(command="msearch")
@ban
@warn
async def search_migu(msg: Message, *args):
    keyword = ' '.join(args)
    if not keyword:
        raise Exception("格式输入有误。\n正确格式为: /msearch {keyword} 或 /搜咪咕 {keyword}")
    else:
        candidates = await msearch_music_by_keyword(music_name=keyword)
        if candidates:
            author_id = msg.author.id
            expire = datetime.datetime.now() + datetime.timedelta(minutes=1)
            candidates_body = {
                "candidates": candidates,
                "expire": expire
            }
            settings.candidates_map.pop(author_id, None)
            settings.candidates_map[author_id] = candidates_body

            select_menu_msg = CardMessage(*CS.searchCard({"migu": candidates}))
            await msg.reply(select_menu_msg)

        else:
            await msg.reply(f"没有任何与关键词: {keyword} 匹配的信息, 试试搜索其他关键字吧")


@bot.command(name='qsearch', aliases=['qq', 'qqsearch', 'searchqq', '搜索QQ', '搜QQ', 'QQ音乐'])
@log(command="qsearch")
@ban
@warn
async def search_qq(msg: Message, *args):
    keyword = ' '.join(args)
    if not keyword:
        raise Exception("格式输入有误。\n正确格式为: /msearch {keyword} 或 /搜咪咕 {keyword}")
    else:
        candidates = await qsearch_music_by_keyword(bot, keyword)
        if candidates:
            author_id = msg.author.id
            expire = datetime.datetime.now() + datetime.timedelta(minutes=1)
            candidates_body = {
                "candidates": candidates,
                "expire": expire
            }
            settings.candidates_map.pop(author_id, None)
            settings.candidates_map[author_id] = candidates_body

            select_menu_msg = CardMessage(*CS.searchCard({"qqmusic": candidates}))
            await msg.channel.send(select_menu_msg)

        else:
            await msg.channel.send(f"没有任何与关键词: {keyword} 匹配的信息, 试试搜索其他关键字吧")


@bot.command(name="select", aliases=["pick", "选择", "选"])
@log(command="select")
@ban
@warn
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
                await msg.channel.send(f"已将 {selected_music.name}-{selected_music.author} 添加到播放列表")


@bot.command(name="list", aliases=["ls", "列表", "播放列表", "队列"])
@log(command="list")
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
                resp += f"[{index + 1}] {this_music.name} - {this_music.author}"
                if index == 0:
                    resp += " <-- 正在播放 -->\n"
                else:
                    resp += "\n"
            await msg.channel.send(resp)
        except Exception as e:
            raise e


@bot.command(name="cut", aliases=["next", "切歌", "下一首", "切"])
@log(command="cut")
@ban
@warn
async def cut_music(msg: Message):
    play_list = list(settings.playqueue)
    if not play_list:
        await msg.channel.send("当前的播放列表为空哦")
    else:
        if len(play_list) == 1:
            await msg.channel.send("正在切歌，请稍候")
            settings.playqueue.popleft()
            await container_handler.stop_container()
            await msg.channel.send("后面没歌了哦")
            settings.played = 0
        else:
            await msg.channel.send("正在切歌，请稍候")
            settings.playqueue.popleft()
            next_music = settings.playqueue[0]
            next_music.endtime = int(datetime.datetime.now().timestamp() * 1000) + next_music.duration
            await msg.channel.send(f"正在为您播放 {next_music.name} - {next_music.author}")
            await container_handler.create_container(next_music.source)

            settings.played = 5000


@bot.command(name="remove", aliases=["rm", "删除", "删"])
@log(command="remove")
@ban
@warn
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
                await msg.channel.send(f"已将歌曲 {removed_music.name}-{removed_music.author} 从播放列表移除")


@bot.command(name='clear', aliases=['清空'])
@log(command='clear')
@ban
@warn
async def clear_playlist(msg: Message):
    if msg.author.id in settings.admin_users:
        length = len(settings.playqueue)
        if not length:
            raise Exception("播放列表中没有任何歌曲哦")
        else:
            await msg.channel.send("正在清空播放列表，请稍候")
            settings.playqueue.clear()
            await container_handler.stop_container()
            await msg.channel.send("播放列表已清空")
            settings.played = 0
    else:
        await msg.channel.send("permission denied")


@bot.command(name="top", aliases=["置顶", "顶"])
@log(command="top")
@ban
@warn
async def make_music_at_top_of_play_list(msg: Message, music_number: str=""):
    play_list = list(settings.playqueue)
    play_list_length = len(play_list)
    if not play_list_length:
        raise Exception("播放列表中没有任何歌曲哦")

    if not music_number:
        await msg.channel.send(CardMessage(CS.topCard(play_list[1:])))
    else:
        music_number = int(music_number)
        if music_number == 1:
            raise Exception("不能置顶正在播放的音乐, 它不是已经在播放了吗?")
        elif music_number > play_list_length:
            raise Exception(f"列表中一共只有 {play_list_length} 首歌, 你不能置顶第 {music_number} 首歌")
        elif music_number <= 0:
            raise Exception(f"输入不合法, 请不要输入0或者负数")
        else:
            to_top_music = play_list[music_number - 1]
            del settings.playqueue[music_number - 1]
            settings.playqueue.insert(1, to_top_music)
            await msg.channel.send(f"已将歌曲 {to_top_music.name}-{to_top_music.author} 在播放列表中置顶")


@bot.command(name="pause", aliases=["暂停"])
@log(command="pause")
@ban
@warn
async def pause(msg: Message):
    await container_handler.pause_container()


@bot.command(name="unpause", aliases=["取消暂停", "继续"])
@log(command="unpause")
@ban
@warn
async def unpause(msg: Message):
    await container_handler.unpause_container()


"""
@bot.command(name="stop", aliases=["停止", "结束"])
async def stop_music(msg: Message):
    await msg.channel.send("正在结束...请稍候")
    await stop_container(settings.container_name)
"""


@bot.command(name="warn")
@log(command="warn")
async def operate_warned_user_list(msg: Message, action: str="", user_id: str=""):
    if msg.author.id in settings.admin_users:
        if action not in ["add", "remove", "list", "rm", "ls"]:
            raise Exception(f"unknown action: {action}")
        if not user_id and action not in ["list", "ls"]:
            raise Exception("missing user id")
        if action in ["add"]:
            settings.warned_user_list.append(user_id)
            await msg.channel.send(f"user: {user_id} has been added to warned user list")
        if action in ["remove", "rm"]:
            if user_id not in settings.warned_user_list:
                raise Exception(f"user: {user_id} is not in warned user list")
            else:
                settings.warned_user_list.remove(user_id)
                await msg.channel.send(f"user {user_id} has been removed from warned user list")
        if action in ["list", "ls"]:
            await msg.channel.send(f"current warned user list is {settings.warned_user_list}")

    else:
        await msg.channel.send("permission denied")


@bot.command(name="ban")
@log(command="ban")
async def operate_banned_user_list(msg: Message, action: str="", user_id: str=""):
    if msg.author.id in settings.admin_users:
        if action not in ["add", "remove", "list", "rm", "ls"]:
            raise Exception(f"unknown action: {action}")
        if not user_id and action not in ["list", "ls"]:
            raise Exception("missing user id")
        if action in ["add"]:
            settings.banned_user_list.append(user_id)
            await msg.channel.send(f"user: {user_id} has been added to banned user list")
        if action in ["remove", "rm"]:
            if user_id not in settings.banned_user_list:
                raise Exception(f"user: {user_id} is not in banned user list")
            else:
                settings.banned_user_list.remove(user_id)
                await msg.channel.send(f"user {user_id} has been removed from banned user list")
        if action in ["list", "ls"]:
            await msg.channel.send(f"current banned user list is {settings.banned_user_list}")

    else:
        await msg.channel.send("permission denied")


@bot.command(name="logout")
@log(command="logout")
async def logout(msg: Message):
    if msg.author.id in settings.admin_users:
        await msg.channel.send("logging out now...")
        raise KeyboardInterrupt()
    else:
        await msg.channel.send("permission denied")


# startup events
@bot.task.add_date()
async def startup_tasks():
    await container_handler.clear_leaked_containers()


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


@bot.task.add_interval(minutes=3)
async def three_minutes_interval_tasks():
    await update_kanban_info(bot=bot)
    # await update_playing_game_status(bot=bot)


@bot.task.add_interval(minutes=20)
async def twenty_minutes_interval_tasks():
    await keep_bot_market_heart_beat()


# buttons reflection event, WIP
from khl import Event,EventTypes
@bot.on_event(EventTypes.MESSAGE_BTN_CLICK)
async def msg_btn_click(b:Bot,event:Event):
    channel = await b.fetch_public_channel(event.body['target_id'])
    user_id = event.body['user_id']
    message = PublicMessage(
        msg_id=event.body['msg_id'],
        _gate_=gate,
        target_id=event.body['target_id'],
        extra={'guild_id': event.body['guild_id'], 'channel_name': channel.name, 'author': {'id': user_id}})
    value = event.body['value']

    now_time = datetime.datetime.now().timestamp() * 1000
    action, *args, end_time = (value.split(":"))
    end_time = int(end_time)

    play_list = list(settings.playqueue)
    play_list_length = len(play_list)

    if action == 'remove':
        music_number = int(args[0])

        if not play_list_length:
            await channel.send("当前的播放列表为空哦")
            try:
                await message.delete()
            except:
                pass
        elif music_number > play_list_length or now_time > end_time:
            await update_cardmessage(message, CardMessage(*CS.MusicListCard(play_list)))
        else:
            del settings.playqueue[music_number - 1]
            new_play_list = list(settings.playqueue)
            await update_cardmessage(message, CardMessage(*CS.MusicListCard(new_play_list)))

    elif action == 'pick':
        pick_number = int(args[0])

        if user_id not in settings.candidates_map:
            try:
                await message.delete()
            except:
                pass
            await channel.send('你的搜索不存在或已过期')
        else:
            candidates = settings.candidates_map[user_id].get("candidates")
            selected_music = candidates[pick_number]
            settings.candidates_map.pop(user_id, None)
            settings.playqueue.append(selected_music)

            await update_cardmessage(message, CardMessage(CS.pickCard(selected_music)))


    elif action == 'top':
        top_number = int(args[0])

        if top_number > play_list_length:
            await update_cardmessage(message, CardMessage(CS.topCard(play_list[1:])))
        else:
            to_top_music = play_list[top_number - 1]
            del settings.playqueue[top_number - 1]
            settings.playqueue.insert(1, to_top_music)
            new_play_list = list(settings.playqueue)
            await update_cardmessage(message, CardMessage(CS.topCard(new_play_list[1:])))

    '''
    elif action == 'cut':
        if not play_list:
            try:
                await message.delete()
            except:
                pass
            await channel.send('当前播放列表为空哦')
        else:
            settings.playqueue.popleft()

            if len(play_list) == 1:
                await container_handler.stop_container()
                await channel.send('后面没歌了哦')
                settings.played = 0
            else:
                next_music = settings.playqueue[0]
                next_music.endtime = int(datetime.datetime.now().timestamp() * 1000) + next_music.duration
                new_play_list = list(settings.playqueue)
                await update_cardmessage(bot, msg_id, str(list(CardMessage(*CS.MusicListCard(new_play_list)))).replace("'", '"'))

                settings.played = 5000'''

    # use action to do something

    # this function is WIP 
##################


async def update_cardmessage(message: Message, content: CardMessage):
    try:
        content_str = json.dumps(content)
        await update_cardmessage_by_bot(bot, message.id, content_str)
    except:
        await message.delete()
        await message.ctx.channel.send(content)


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
