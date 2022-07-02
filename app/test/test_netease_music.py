import asyncio
from unittest import IsolatedAsyncioTestCase, TestCase

from app.music_new.netease.netease_music import *

SESSION_CLOSE_DELAY = 0
SONG_ID_PLAYABLE = 36226134
SONG_ID_NOT_PLAYABLE = 1866768982
SONG_ID_INVALID = 0


class TestNeteaseMusicAPI(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.sess = aiohttp.ClientSession()

    async def asyncTearDown(self) -> None:
        # shortly delay before closing for the best practice:
        # https://docs.aiohttp.org/en/latest/client_advanced.html#graceful-shutdown
        await asyncio.sleep(SESSION_CLOSE_DELAY)
        await self.sess.close()

    async def test_search_music(self):
        details = await search_music(self.sess, "Duvet")
        self.assertNotEqual(details, [])

    async def test_batch_fetch_basic_details(self):
        details = await batch_fetch_basic_details(self.sess, SONG_ID_PLAYABLE, SONG_ID_NOT_PLAYABLE, SONG_ID_INVALID)
        self.assertIsNotNone(details.get(SONG_ID_PLAYABLE))
        self.assertIsNotNone(details.get(SONG_ID_NOT_PLAYABLE))
        self.assertIsNone(details.get(SONG_ID_INVALID))

    async def test_batch_fetch_media_urls(self):
        details = await batch_fetch_media_urls(self.sess, SONG_ID_PLAYABLE, SONG_ID_NOT_PLAYABLE, SONG_ID_INVALID)
        self.assertIsNotNone(details.get(SONG_ID_PLAYABLE))
        self.assertIsNone(details.get(SONG_ID_NOT_PLAYABLE))
        self.assertIsNone(details.get(SONG_ID_INVALID))


class TestNeteaseMusic(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.sess = aiohttp.ClientSession()

    async def asyncTearDown(self) -> None:
        await asyncio.sleep(SESSION_CLOSE_DELAY)
        await self.sess.close()

    async def test_music_playable(self):
        music = await NeteaseMusicPlatform().play_by_id(self.sess, SONG_ID_PLAYABLE)
        self.assertEqual(music.name,
                         'Liebesträume - 3 Notturnos für das Pianoforte S.541:O lieb, so lang du lieben kannst!')
        self.assertEqual(music.artists, ['Leslie Howard'])
        self.assertEqual(await music.duration_ms(self.sess), 253600)
        await assert_is_image_url(self, await music.cover_url(self.sess))
        self.assertTrue(await music.playable(self.sess))
        await assert_is_music_url(self, await music.media_url(self.sess))

    async def test_music_not_playable(self):
        music = await NeteaseMusicPlatform().play_by_id(self.sess, SONG_ID_NOT_PLAYABLE)
        self.assertEqual(music.name, 'BEACON')
        self.assertEqual(music.artists, ['平沢進'])
        self.assertEqual(await music.duration_ms(self.sess), 226146)
        await assert_is_image_url(self, await music.cover_url(self.sess))
        self.assertFalse(await music.playable(self.sess))
        self.assertIsNone(await music.media_url(self.sess))

    async def test_music_invalid(self):
        music = await NeteaseMusicPlatform().play_by_id(self.sess, SONG_ID_INVALID)
        self.assertIsNone(music)


async def assert_is_image_url(self: TestCase, url):
    self.assertIsInstance(url, str)
    async with aiohttp.ClientSession() as sess:
        async with sess.get(url) as resp:
            self.assertTrue(resp.status, 200)
            self.assertTrue(resp.headers.get('Content-Type').startswith('image/'))
            self.assertTrue(int(resp.headers.get('Content-Length')) > 0)


async def assert_is_music_url(self: TestCase, url):
    self.assertIsInstance(url, str)
    async with aiohttp.ClientSession() as sess:
        async with sess.get(url) as resp:
            self.assertTrue(resp.status, 200)
            self.assertTrue(resp.headers.get('Content-Type').startswith('audio/'))
            self.assertTrue(int(resp.headers.get('Content-Length')) > 0)
