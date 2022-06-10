import uuid
import traceback

from loguru import logger
from khl import Message

DEBUG = False


def loguru_decorator(func):
    async def wrapped_function(msg: Message, *args, **kwargs):
        log_id = uuid.uuid4()
        logger.info(f"user: {msg.author.username} called func {func} with args {args} and {kwargs}, log_id: {log_id}")
        try:
            msg.ctx.log_id = log_id
            await func(msg, *args, **kwargs)
        except Exception as e:
            logger.error(f"error occurred, msg: {e}, log_id: {log_id}, traceback: {traceback.format_exc()}")
            try:
                if DEBUG:
                    await msg.channel.send(traceback.format_exc())
                else:
                    await msg.channel.send(str(e))
            except Exception as e:
                logger.critical(f"fatal error, log_id: {log_id}, traceback: {traceback.format_exc()}")
    return wrapped_function
