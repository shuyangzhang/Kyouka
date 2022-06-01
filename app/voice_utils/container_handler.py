import docker


IMAGE_NAME = "shuyangzhang/khl-voice"
CONTAINER_NAME = "kyouka"

CLIENT = docker.from_env()

async def create_container(token: str, channel: str, source: str, repeat: str):
    env_dict = {
        "TOKEN": token,
        "CHANNEL": channel,
        "SOURCE": source,
        "REPEAT": repeat,
    }
    print(env_dict)
    CLIENT.containers.run(
        IMAGE_NAME,
        auto_remove = True,
        environment = env_dict,
        tty = True,
        detach = True,
        name = CONTAINER_NAME
    )

async def stop_container():
    try:
        container = CLIENT.containers.get(CONTAINER_NAME)
        container.stop()
    except docker.errors.NotFound:
        print("kyouku is not running")

async def pause_container():
    try:
        container = CLIENT.containers.get(CONTAINER_NAME)
        container.pause()
    except docker.errors.NotFound:
        print("kyouku is not running")

async def unpause_container():
    try:
        container = CLIENT.containers.get(CONTAINER_NAME)
        container.unpause()
    except docker.errors.NotFound:
        print("kyouku is not running")

