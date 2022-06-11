import docker
from loguru import logger


IMAGE_NAME = "shuyangzhang/khl-voice"

CLIENT = docker.from_env()

async def create_container(token: str, channel: str, source: str, repeat: str, container_name: str):
    env_dict = {
        "TOKEN": token,
        "CHANNEL": channel,
        "SOURCE": source,
        "REPEAT": repeat,
    }
    logger.debug(f"{env_dict}")
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
