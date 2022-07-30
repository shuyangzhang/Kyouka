import datetime
from tkinter import Image

from typing import Dict
from khl.card import Card
from khl.card.module import Module
from khl.card.interface import Types, _Module
from khl.card.element import Element
from khl.card.struct import Struct
from khl.card.color import Color

###################### music

from typing import Tuple

from app.music.music import Music

__MUSIC_LIST_TILE_COLOR = "#9b59b6"
__MUSIC_LIST_PLAYING_MUSIC_COLOR = "#a29bfe"


NO_COVER_URL = 'https://img.kookapp.cn/assets/2022-07/2rM6IYtAu53uw3uw.png'

ASSETS = {
    'netease_radio': {
        'icon': 'https://img.kookapp.cn/assets/2022-07/RxgxZS3tIK00w00w.png',
        'text': '网易云音乐',
        'url': '',
        'color': ''
    },
    'netease': {
        'icon': 'https://img.kookapp.cn/assets/2022-07/RxgxZS3tIK00w00w.png',
        'text': '网易云音乐',
        'url': 'https://music.163.com/#/song?id={}',
        'color': 'dd001a'
    },
    'qqmusic': {
        'icon': 'https://img.kookapp.cn/assets/2022-07/VLtsP2quEZ00w00w.png',
        'text': 'QQ音乐',
        'url': 'https://y.qq.com/n/ryqq/songDetail/{}',
        'color': 'ffdc01'
    },
    'migu': {
        'icon': 'https://img.kookapp.cn/assets/2022-07/2VklLsY5XP01s01s.png',
        'text': '咪咕音乐',
        'url': 'https://music.migu.cn/v3/music/song/{}',
        'color': '#ed3c65'
    },
    'bili': {
        'icon': 'https://img.kookapp.cn/assets/2022-07/SZQ8mFm2Q700w00w.png',
        'text': '哔哩哔哩',
        'url': 'https://www.bilibili.com/video/{}',
        'color': ''
    },
    'osu': {
        'icon': 'https://img.kookapp.cn/assets/2022-07/vSPG7hAPrZ00w00w.png',
        'text': 'osu!',
        'url': 'https://osu.ppy.sh/beatmapsets/{}',
        'color': '#e3609a'
    }
}


def NowMusicCard(music_list: list[Music]) -> Card:
    # playing music card
    first_music = music_list[0]
    text = ASSETS[first_music.website]['text']
    url = ASSETS[first_music.website]['url'].format(first_music.music_id)

    if text and url:
        source_url = f'[{text}]({url})'
    elif text and not url:
        # netease radio
        source_url = text
    else:
        source_url = ''

    playing_music_card = Card(theme=Types.Theme.INFO, color=Color(hex=__MUSIC_LIST_PLAYING_MUSIC_COLOR))
    playing_music_card.append(
        # Module.Section(
        #     Element.Text(f":notes:  **当前歌曲**", type=Types.Text.KMD),
        #     Element.Button('切歌', 'cut:-1:-1', theme=Types.Theme.DANGER)
        # )
        Module.Header(f":notes:  当前歌曲")
    )
    playing_music_card.append(Module.Divider())
    image_url = first_music.cover_url
    playing_music_card.append(
        Module.Section(
            Element.Text(
                f"**{first_music.name}  -  {first_music.author}**\n{f'专辑：{first_music.album}' if first_music.album else ''}\n来源：{source_url}",
                type=Types.Text.KMD
            ),
            accessory=Element.Image(
                src = image_url if image_url!="" else NO_COVER_URL,
                size= Types.Size.SM
            ),
            mode=Types.SectionMode.RIGHT
        )
    )

    end_time_int = first_music.endtime
    start_time_int = (end_time_int if end_time_int != -1 else datetime.datetime.now().timestamp()
                      ) - first_music.duration
    end_time = datetime.datetime.fromtimestamp(end_time_int / 1e3) if end_time_int != -1 else datetime.datetime.now()
    start_time = datetime.datetime.fromtimestamp(start_time_int / 1e3)
    playing_music_card.append(
        Module.Countdown(
            end = end_time,
            mode = Types.CountdownMode.SECOND,
            start=start_time,
        )
    )

    return playing_music_card


def MusicListCard(music_list: list[Music]) -> Tuple[Card, Card]:
    """
    返回音乐列表card
    :param music_list:进入数据结构大致为，： music_list[5] = [
    ['music_name1','music_author','music_url' , 500, 1654354800000],
    ['music_name2','music_author','music_url','music_length',-1],
    ['music_name3','music_author','music_url','music_length',-1],
    ...
]
    :return:
    """
    first_music = music_list[0]
    end_time_int = first_music.endtime
    end_time = datetime.datetime.fromtimestamp(end_time_int / 1e3) if end_time_int != -1 else datetime.datetime.now()

    # 剩余列表
    remaining_list_card = Card(theme=Types.Theme.SECONDARY)
    remaining_list_card.append(
        Module.Header(f":star2:  剩余歌曲")
    )
    for index,one_music_des in enumerate( music_list[1:]):
        image_url = one_music_des.cover_url
        remaining_list_card.append(Module.Divider())
        remaining_list_card.append(
            Module.Section(
                Element.Text(
                    f"**({index + 2})    {one_music_des.name} - {one_music_des.author}**",
                    type=Types.Text.KMD
                ),
                accessory=Element.Button('删除', f"remove:{index+2}:{end_time}", theme=Types.Theme.DANGER)
            )
        )
        remaining_list_card.append(
            Module.Context(
                Element.Image(image_url),
                Element.Text(f' | 来源：{ASSETS[one_music_des.website]["text"]} '),
                Element.Image(ASSETS[one_music_des.website]['icon'])
            )
        )

    return NowMusicCard(music_list), remaining_list_card


def HelpCard() -> Card:
    card = Card(theme=Types.Theme.INFO, size=Types.Size.LG)
    # title
    card.append(Module.Header(":watermelon:  镜华Kyouka 操作指南 v0.7.0 20220703 :watermelon:"))
    card.append(Module.Section(Element.Text(":bangbang: 播放歌曲前务必先绑定语音频道哦！")))

    # base command
    card.append(
        Module.Section(
            Element.Text(
"""
:headphones:  **绑定语音频道**  :headphones: (下列方式二选一)
`/comehere` - 绑定你所在的语音频道 [推荐]
`/channel {channel_id}` - 通过语音频道ID绑定
"""
                , type=Types.Text.KMD
            )
        )
    )

    # other command
    card.append(
        Module.Section(
            Element.Text(
"""
:musical_note:  **音乐指令**  :musical_note:
`/play {music_name}` - 点歌
`/search {keyword}` - 搜索歌曲
`/msearch {keyword}` - 搜索咪咕音乐中的歌曲
`/qsearch {keyword}` - 搜索QQ音乐中的歌曲
`/osearch {keyword}` - 搜索osu!中的歌曲
`/select {search_list_id}` - 从搜索的列表中选择歌曲
`/bilibili {bili_video_url}` - 点播B站视频 [实验功能, 暂不稳定]
`/list` - 查看播放列表
`/cut` - 切歌
`/playlist {playlist_url}` - 导入网易云音乐歌单
`/album {album_url}` - 导入网易云音乐专辑
`/radio {radio_url}` - 导入网易云电台
`/remove {list_id}` - 删除歌单中的歌曲
`/top {list_id}` - 播放列表中的歌曲置顶
"""
                , type=Types.Text.KMD
            )
        )
    )

    card.append(
        # InviteModule()
        Module.Invite('oHRMIL')
    )

    card.append(
        Module.Context(
            Element.Text(
"""
如有任何问题、意见、建议，或需要邀请、私有部署，或想一起开发镜华Kyouka，欢迎加入 镜华Kyouka 点歌机器人 官方服务器
或 联系开发者 (met)693543263(met)
"""
                , type=Types.Text.KMD
            )
        )
    )

    return card

def searchCard(music_dict: dict) -> Card:
    return_card = []
    music_list: list[Music] = []
    end_time = str(datetime.datetime.now() + datetime.timedelta(minutes=1)).replace(':', '-')

    for value in music_dict.values():
        music_list += value

    for key in music_dict.keys():
        card = Card(color=Color(hex=ASSETS[key]['color']))
        search_list: list[Music] = music_dict[key]
        for music in search_list:
            card.append(
                Module.Section(
                    Element.Text(f'** ({music_list.index(music) + 1}) {music.name} - {music.author}**', type=Types.Text.KMD),
                    Element.Button('点歌', f'pick:{str(music_list.index(music))}:{end_time}', theme=Types.Theme.SUCCESS)
                    )
                )
            card.append(Module.Context(
                Element.Image(music.cover_url),
                Element.Text(f' {music.album}')
            ))
            card.append(Module.Divider())
        card.append(
            Module.Context(
                Element.Text(f'来自*{ASSETS[key]["text"]}* ', Types.Text.KMD),
                Element.Image(ASSETS[key]["icon"]),
                Element.Text('\n输入 /select {编号} 或 /选 {编号} 即可加入歌单(一分钟内操作有效)')
            )
        )
        return_card.append(card)

    return (card for card in return_card)

def pickCard(music: Music) -> Card:
    text = ASSETS[music.website]['text']
    url = ASSETS[music.website]['url'].format(music.music_id)
    source_url = f'[{text}]({url})'

    card = Card(Module.Header(f'已将 {music.name} 添加到播放列表'), Module.Divider())
    card.append(
        Module.Section(
            Element.Text(
                f"**{music.name}  -  {music.author}**\n{f'专辑：{music.album}' if music.album else ''}\n来源：{source_url}",
                type=Types.Text.KMD
            ),
            accessory=Element.Image(
                src = music.cover_url if music.cover_url !="" else NO_COVER_URL,
                size= Types.Size.SM
            ),
            mode=Types.SectionMode.RIGHT
        )
    )

    return card

def topCard(music_list: list[Music]) -> Card:
    card = Card(theme=Types.Theme.SECONDARY)
    card.append(
        Module.Header(f"置顶")
    )
    for index, one_music_des in enumerate(music_list):
        image_url = one_music_des.cover_url
        card.append(Module.Divider())
        card.append(
            Module.Section(
                Element.Text(
                    f"**({index + 2})    {one_music_des.name} - {one_music_des.author}**",
                    type=Types.Text.KMD
                ),
                accessory=Element.Button('置顶', f"top:{index+2}:-1", theme=Types.Theme.INFO)
            )
        )
        card.append(
            Module.Context(
                Element.Image(image_url),
                Element.Text(f' | 来源：{ASSETS[one_music_des.website]["text"]} '),
                Element.Image(ASSETS[one_music_des.website]['icon'])
            )
        )

    return card