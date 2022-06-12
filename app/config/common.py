import collections

from pydantic import BaseSettings
from typing import List


class CommonSettings(BaseSettings):
    debug: bool = False

    admin_users: List[str] = []

    file_logger: bool = True

    token: str = ""
    channel: str = ""
    container_name: str = ""

    re_prefix_switch: bool = False
    re_prefix_enable: bool = True
    re_prefix_inbegin: bool = True

    played: int = 0   # ms
    playqueue: collections.deque = collections.deque()
    lock: bool = False

    candidates_map: dict = {}
    candidates_lock: bool = False

    class Config:
        env_file = ".env"


settings = CommonSettings()
