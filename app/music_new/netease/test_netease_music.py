import asyncio
from unittest import IsolatedAsyncioTestCase
from urllib.parse import urlparse

from app.music_new.netease.netease_music import *

SONG_ID_PLAYABLE = 36226134
SONG_ID_NOT_PLAYABLE = 1866768982
SONG_ID_INVALID = 0


class TestNeteaseMusic(IsolatedAsyncioTestCase):
    async def test_music_playable(self):
        music = NeteaseMusic(SONG_ID_PLAYABLE)
        self.assertEqual(await music.name,
                         'Liebesträume - 3 Notturnos für das Pianoforte S.541:O lieb, so lang du lieben kannst!')
        self.assertEqual(await music.artists, ['Leslie Howard'])
        self.assertEqual(await music.duration_ms, 253600)
        segments = urlparse(await music.cover_url)
        self.assertNotEqual(segments.netloc, '')
        self.assertNotEqual(segments.path, '')
        self.assertNotEqual(segments.query, '')
        self.assertTrue(await music.playable)
        self.assertIsNotNone(await music.media_url)

    async def test_music_aio_efficiency_playable(self):
        music = NeteaseMusic(SONG_ID_PLAYABLE)
        await asyncio.gather(music.name, music.artists, music.duration_ms, music.cover_url)
        assert music.requestors[DetailRequestor.__name__]._request_counter == 1
        await asyncio.gather(music.playable, music.media_url)
        assert music.requestors[SourceRequestor.__name__]._request_counter == 1

    async def test_music_not_playable(self):
        music = NeteaseMusic(SONG_ID_NOT_PLAYABLE)
        self.assertEqual(await music.name, 'BEACON')
        self.assertEqual(await music.artists, ['平沢進'])
        self.assertEqual(await music.duration_ms, 226146)
        segments = urlparse(await music.cover_url)
        self.assertNotEqual(segments.netloc, '')
        self.assertNotEqual(segments.path, '')
        self.assertNotEqual(segments.query, '')
        self.assertFalse(await music.playable)
        self.assertIsNone(await music.media_url)

    async def test_music_aio_efficiency_not_playable(self):
        music = NeteaseMusic(SONG_ID_NOT_PLAYABLE)
        await asyncio.gather(music.name, music.artists, music.duration_ms, music.cover_url,
                             music.playable, music.media_url)
        assert music.requestors[DetailRequestor.__name__]._request_counter == 1
        assert music.requestors[SourceRequestor.__name__]._request_counter == 1

    async def test_music_invalid(self):
        with self.assertRaisesRegex(Exception, r'no music found corresponding to id \d+\.'):
            await NeteaseMusic(SONG_ID_INVALID).name

    async def test_music_aio_efficiency_invalid(self):
        music = NeteaseMusic(SONG_ID_INVALID)
        with self.assertRaisesRegex(Exception, r'no music found corresponding to id \d+\.'):
            await asyncio.gather(music.name, music.artists, music.duration_ms, music.cover_url,
                                 music.playable, music.media_url)
        assert music.requestors[DetailRequestor.__name__]._request_counter == 1
        assert music.requestors[SourceRequestor.__name__]._request_counter == 1
