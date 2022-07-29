import io
import aiohttp
from loguru import logger
from PIL import Image
from khl import Bot


async def webp2jpeg(bot: Bot, webp_url: str):
    webp_buffer = await get_webp_stream(webp_url)
    webp_object = io.BytesIO(webp_buffer)
    image = Image.open(webp_object).convert("RGB")
    output_obj = io.BytesIO()
    image.save(output_obj, "JPEG")
    jpeg_url = await jpeg_obj2url(bot, output_obj)
    logger.debug(f"jpeg url = {jpeg_url}")
    return jpeg_url

async def get_webp_stream(url: str): 
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                return await resp.read()
            return None

async def jpeg_obj2url(bot: Bot, jpeg_obj: io.BytesIO):
    image_bytes = jpeg_obj.getvalue()
    url = await bot.create_asset(image_bytes)
    return url

if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(webp2jpeg("http://y.qq.com/music/photo_new/T002R300x300M000001uaPM93kxk1R.jpg"))
