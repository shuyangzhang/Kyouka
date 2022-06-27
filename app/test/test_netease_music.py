from unittest import IsolatedAsyncioTestCase

from app.music_new.netease.netease_music import *

SONG_ID_PLAYABLE = 36226134
SONG_ID_NOT_PLAYABLE = 1866768982
SONG_ID_INVALID = 0


class TestNeteaseMusicPlatform(IsolatedAsyncioTestCase):
    # FIXME
    pass


class TestNeteaseMusic(IsolatedAsyncioTestCase):
    async def test_music_playable(self):
        music = await NeteaseMusicPlatform().play_by_id(SONG_ID_PLAYABLE)
        self.assertEqual(music.name,
                         'Liebesträume - 3 Notturnos für das Pianoforte S.541:O lieb, so lang du lieben kannst!')
        self.assertEqual(music.artists, ['Leslie Howard'])
        self.assertEqual(await music.duration_ms, 253600)
        # TODO: find a way to test cover url
        self.assertTrue(await music.playable)
        self.assertIsNotNone(await music.media_url)

    async def test_music_not_playable(self):
        music = await NeteaseMusicPlatform().play_by_id(SONG_ID_NOT_PLAYABLE)
        self.assertEqual(music.name, 'BEACON')
        self.assertEqual(music.artists, ['平沢進'])
        self.assertEqual(await music.duration_ms, 226146)
        # TODO: find a way to test cover url
        # FIXME: fix ResourceWarning
        self.assertFalse(await music.playable)
        self.assertIsNone(await music.media_url)

    async def test_music_invalid(self):
        music = await NeteaseMusicPlatform().play_by_id(SONG_ID_INVALID)
        self.assertIsNone(music)
