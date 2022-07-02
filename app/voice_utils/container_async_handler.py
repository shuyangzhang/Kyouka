import uuid
import aiodocker

from loguru import logger
from aiodocker.exceptions import DockerError
from app.config.common import settings


IMAGE_NAME = "shuyangzhang/khl-voice"


class ContainerHandler:
    def __init__(self):
        self.client = aiodocker.Docker()
        self.previous_container_name = ""
        self.current_container_name = "NOT_INITIALIZED"

    def _generate_container_name(self):
        self.previous_container_name = self.current_container_name
        new_name_suffix = str(uuid.uuid4())[:8]
        self.current_container_name = f"{settings.container_name}-{new_name_suffix}"

    async def clear_leaked_containers(self):
        logger.info("start clearing leaked containers")
        leaked_containers = []
        for this_container in (await self.client.containers.list()):
            this_container_name = this_container._container.get("Names", [""])[0][1:]
            if this_container_name.startswith(f"{settings.container_name}-"):
                leaked_containers.append(this_container_name)
        logger.info(f"leaked containers: {leaked_containers}")
        for this_leaked_container in leaked_containers:
            await self.stop_container(container_name=this_leaked_container)
        logger.info(f"clearing succeed")

    async def create_container(self, source: str, repeat: str="false"):
        self._generate_container_name()
        env_list = [f"TOKEN={settings.token}", f"CHANNEL={settings.channel}", f"SOURCE={source}", f"REPEAT={repeat}"]
        config = {
            "Image": IMAGE_NAME,
            "AttachStdin": False,
            "AttachStdout": False,
            "AttachStderr": False,
            "Tty": True,
            "OpenStdin": False,
            "HostConfig": {
                "AutoRemove": True
            },
            "Env": env_list,
        }
        logger.debug(f"{config}")
        await self.client.containers.run(config=config, name=self.current_container_name)
        await self.stop_container(container_name=self.previous_container_name)
    
    async def stop_container(self, container_name: str=""):
        try:
            if not container_name:
                container_name = self.current_container_name
            container = await self.client.containers.get(container_name)
            await container.stop()
        except DockerError:
            logger.warning(f"{container_name} is not running")
    
    async def pause_container(self):
        try:
            container = await self.client.containers.get(self.current_container_name)
            await container.pause()
        except DockerError:
            logger.warning(f"{self.current_container_name} is not running")
    
    async def unpause_container(self):
        try:
            container = await self.client.containers.get(self.current_container_name)
            await container.unpause()
        except DockerError:
            logger.warning(f"{self.current_container_name} is not running")
    

container_handler = ContainerHandler()


"""
CLIENT = aiodocker.Docker()

async def create_container(token: str, channel: str, source: str, repeat: str, container_name: str):
    env_list = [f"TOKEN={token}", f"CHANNEL={channel}", f"SOURCE={source}", f"REPEAT={repeat}"]
    config = {
        "Image": IMAGE_NAME,
        "AttachStdin": False,
        "AttachStdout": False,
        "AttachStderr": False,
        "Tty": True,
        "OpenStdin": False,
        "HostConfig": {
            "AutoRemove": True
        },
        "Env": env_list,
    }
    logger.debug(f"{config}")
    await CLIENT.containers.run(config=config, name=container_name)

async def stop_container(container_name: str):
    try:
        container = await CLIENT.containers.get(container_name)
        await container.stop()
    except DockerError:
        logger.warning(f"{container_name} is not running")

async def pause_container(container_name: str):
    try:
        container = await CLIENT.containers.get(container_name)
        await container.pause()
    except DockerError:
        logger.warning(f"{container_name} is not running")

async def unpause_container(container_name: str):
    try:
        container = await CLIENT.containers.get(container_name)
        await container.unpause()
    except DockerError:
        logger.warning(f"{container_name} is not running")
"""