import collections

from pydantic import BaseSettings
from typing import List

from app.music.music import Music


class CommonSettings(BaseSettings):
    debug: bool = False

    admin_users: List[str] = []

    file_logger: bool = True

    token: str = ""
    channel: str = ""
    container_name: str = ""
    bot_name: str = "镜华 Kyouka"

    public: bool = False
    kanban: bool = False
    kanban_channel: str = ""

    local_bproxy: bool = False
    local_bproxy_url: str = ""

    bot_market_heart_beat: bool = False
    bot_market_uuid: str = ""

    warned_user_list: List[str] = []
    banned_user_list: List[str] = []

    re_prefix_switch: bool = False
    re_prefix_enable: bool = True
    re_prefix_inbegin: bool = True

    played: int = 0   # ms
    playqueue: collections.deque[Music] = collections.deque()
    lock: bool = False

    candidates_map: dict = {}
    candidates_lock: bool = False

    class Config:
        env_file = ".env"


settings = CommonSettings()
