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


ASSETS = {
    'netease_radio': ['https://img.kookapp.cn/assets/2022-07/RxgxZS3tIK00w00w.png', '网易云音乐'],
    'netease': ['https://img.kookapp.cn/assets/2022-07/RxgxZS3tIK00w00w.png', '网易云音乐'],
    'qqmusic': ['https://img.kookapp.cn/assets/2022-07/VLtsP2quEZ00w00w.png', 'QQ音乐'],
    'migu': ['https://img.kookapp.cn/assets/2022-07/2VklLsY5XP01s01s.png', '咪咕音乐'],
    'bili': ['https://img.kookapp.cn/assets/2022-07/SZQ8mFm2Q700w00w.png', '哔哩哔哩'],
    'osu': ['https://img.kookapp.cn/assets/2022-07/vSPG7hAPrZ00w00w.png', 'osu!']
}

NETEASE_MUSIC = 'https://music.163.com/#/song?id={}'
QQ_MUSIC = 'https://y.qq.com/n/ryqq/songDetail/{}'
MIGU_MUSIC = 'https://music.migu.cn/v3/music/song/{}'
BILIBILI = 'https://www.bilibili.com/video/{}'
OSU = 'https://osu.ppy.sh/beatmapsets/{}'


class InviteModule(_Module):
    _tyep = "invite"

    def __init__ (self):
        super().__init__(Types.Theme.NA, Types.Size.NA)

    @property
    def _repr(self) -> Dict:
        return {
            "type": "invite",
            "code": "https://kaihei.co/oHRMIL"
        }


def NowMusicCard(music_list: list[Music]) -> Card:
    # playing music card
    first_music = music_list[0]
    text = ASSETS[first_music.website][1]
    url = ''
    if first_music.website == 'netease':
        url = NETEASE_MUSIC.format(first_music.music_id)
    elif first_music.website == 'qqmusic':
        url = QQ_MUSIC.format(first_music.music_id)
    elif first_music.website == 'migu':
        url = MIGU_MUSIC.format(first_music.music_id)
    elif first_music.website == 'bili':
        url = BILIBILI.format(first_music.music_id)
    elif first_music.website == 'osu':
        url = OSU.format(first_music.music_id)

    if text and url:
        source_url = f'[{text}]({url})'
    elif text and not url:
        # netease radio
        source_url = text
    else:
        source_url = ''

    playing_music_card = Card(theme=Types.Theme.INFO, color=Color(hex=__MUSIC_LIST_PLAYING_MUSIC_COLOR))
    playing_music_card.append(
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
                src = image_url if image_url!="" else "http://p2.music.126.net/e5cvcdgeosDKTDrkTfZXnQ==/109951166155165682.jpg",
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

    # cut button
    """
    playing_music_card.append(
        Module.ActionGroup(
            Element.Button(
                text = "               切歌               ",
                value='cut:',
                theme=Types.Theme.PRIMARY
            )
        )
    )
    """

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
                accessory=Element.Button('删除', f"remove:{index+2}", theme=Types.Theme.DANGER)
            )
        )
        remaining_list_card.append(
            Module.Context(
                Element.Image(image_url),
                Element.Text(f' | 来源：{ASSETS[one_music_des.website][1]} '),
                Element.Image(ASSETS[one_music_des.website][0])
            )
        )
        """
        remaining_list_card.append(
            Module.ActionGroup(
                Element.Button(
                    text = "置顶",
                    value= f"top:{index+2}",
                    theme=Types.Theme.PRIMARY
                ),
                Element.Button(
                    text = "删除",
                    value= f"remove:{index+2}",
                    theme=Types.Theme.DANGER
                )
            )
        )
        """

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
        InviteModule()
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
