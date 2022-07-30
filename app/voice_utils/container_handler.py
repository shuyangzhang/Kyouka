import docker
import traceback
from loguru import logger

from app.bot import bot


IMAGE_NAME = "shuyangzhang/khl-voice"

CLIENT = docker.from_env()

BUSY_STATUS_GAME_ID = 407348
FREE_STATUS_GAME_ID = 407350

async def set_playing_game_status_by_bot(game_id: int):
    try:
        await bot.update_playing_game(game=game_id, data_type=1)
        logger.info(f"playing status is updated to {game_id} successfully.")
    except Exception as e:
        logger.error(f"failed to update playing status, error msg: {e}, traceback: {traceback.format_exc()}")

async def create_container(token: str, channel: str, source: str, repeat: str, container_name: str):
    env_dict = {
        "TOKEN": token,
        "CHANNEL": channel,
        "SOURCE": source,
        "REPEAT": repeat,
    }
    logger.debug(f"{env_dict}")
    await set_playing_game_status_by_bot(BUSY_STATUS_GAME_ID)
    CLIENT.containers.run(
        IMAGE_NAME,
        auto_remove = True,
        environment = env_dict,
        tty = True,
        detach = True,
        name = container_name
    )

async def stop_container(container_name: str):
    try:
        container = CLIENT.containers.get(container_name)
        container.stop()
        await set_playing_game_status_by_bot(FREE_STATUS_GAME_ID)
    except docker.errors.NotFound:
        logger.warning(f"{container_name} is not running")

async def pause_container(container_name: str):
    try:
        container = CLIENT.containers.get(container_name)
        container.pause()
    except docker.errors.NotFound:
        logger.warning(f"{container_name} is not running")

async def unpause_container(container_name: str):
    try:
        container = CLIENT.containers.get(container_name)
        container.unpause()
    except docker.errors.NotFound:
        logger.warning(f"{container_name} is not running")
