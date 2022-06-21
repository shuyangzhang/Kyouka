class Music:
    def __init__(self, name: str, author: str, source: str, duration: int, cover_url: str):
        self.name = name
        self.author = author
        self.source = source
        self.duration = duration
        self.endtime = -1
        self.cover_url = cover_url

    def __str__(self):
        return f'Music({self.name}, {self.author}, {self.source}, {self.duration}, {self.endtime}, {self.cover_url})'

    def __getitem__(self, item):
        return self.name
