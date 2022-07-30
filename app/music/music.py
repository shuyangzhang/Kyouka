from typing import Union

class Music:
    def __init__(self, music_id: Union[int, str], name: str, author: str, source: str, duration: int, album: str, cover_url: str, website: str):
        self.music_id = music_id
        self.name = name
        self.author = author
        self.source = source
        self.duration = duration
        self.endtime = -1
        self.album = album
        self.cover_url = cover_url
        self.website = website

    def __str__(self):
        return f'Music({self.music_id}, {self.name}, {self.author}, {self.source}, {self.duration}, {self.endtime}, {self.album}, {self.cover_url}, {self.website})'

    def __getitem__(self, item):
        return self.name
