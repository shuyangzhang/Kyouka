import datetime

from khl.card import Card
from khl.card.module import Module
from khl.card.interface import Types
from khl.card.element import Element
from khl.card.struct import Struct
from khl.card.color import Color

from enum import Enum
from typing import Tuple

def NowMusicCard(music_list:list) -> Card:
    # playing music card
    first_music = music_list[0]
    playing_music_card = Card(theme=Types.Theme.INFO, color=Color(hex=__MUSIC_LIST_PLAYING_MUSIC_COLOR))
    playing_music_card.append(
        Module.Header(f":notes:  当前歌曲")
    )

    playing_music_card.append(
        Module.Section(
            Element.Text(
                f"**  {first_music[__MusicListIndex.MUSIC_NAME.value]}  -  {first_music[__MusicListIndex.MUSIC_AUTHOR.value]}**",
                type=Types.Text.KMD
            ),
            accessory=Element.Image(
                #src=first_music[__MusicListIndex.MUSIC_PIC_URL.value]
                src="http://p2.music.126.net/e5cvcdgeosDKTDrkTfZXnQ==/109951166155165682.jpg"
            ),
            mode=Types.SectionMode.LEFT
        )
    )

    end_time_int = first_music[__MusicListIndex.MUSIC_ENDTIME.value]
    start_time_int = (end_time_int if end_time_int!=-1 else datetime.datetime.now().timestamp()) - first_music[__MusicListIndex.MUSIC_LENGTH.value]
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
    playing_music_card.append(
        Module.ActionGroup(
            Element.Button(
                text = "               切歌               ",
                value='cut:',
                theme=Types.Theme.PRIMARY
            )
        )
    )

    return playing_music_card

def MusicListCard(music_list:list) -> Tuple[Card,Card]:
    """
    返回音乐列表card
    :param music_list:进入数据结构大致为，： music_list[5] = [
    ['music_name1','music_author','music_url','music_length',1654354800000],
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
        remaining_list_card.append(
            Module.Section(
                Element.Text(
                    f"**    ({index+2})    {one_music_des[__MusicListIndex.MUSIC_NAME.value]} - {one_music_des[__MusicListIndex.MUSIC_AUTHOR.value]}**",
                    type=Types.Text.KMD
                )
            )
        )
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
        remaining_list_card.append(Module.Divider())

    return NowMusicCard(music_list), remaining_list_card
