import uuid
import traceback

from loguru import logger
from khl import Message
from app.config.common import settings

def loguru_decorator_factory(command: str=""):
    def loguru_decorator(func):
        async def wrapped_function(msg: Message, *args, **kwargs):
            log_id = uuid.uuid4()
            logger.info(f"user: {msg.author.username} user_id: {msg.author.id} in guild_id: {msg.ctx.guild.id} "
                        f"used command {command} with args {args} and {kwargs}, log_id: {log_id}")
            try:
                msg.ctx.log_id = log_id
                await func(msg, *args, **kwargs)
            except Exception as e:
                logger.error(f"error occurred, msg: {e}, log_id: {log_id}, traceback: {traceback.format_exc()}")
                try:
                    if settings.debug:
                        await msg.channel.send(traceback.format_exc())
                    else:
                        await msg.channel.send(str(e))
                except Exception as e:
                    logger.critical(f"fatal error, log_id: {log_id}, traceback: {traceback.format_exc()}")
        return wrapped_function
    return loguru_decorator