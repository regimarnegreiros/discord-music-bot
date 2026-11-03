from models.song import Song

class TrackQueue:
    def __init__(self) -> None:
        self.history: list[Song] = []
        self.current: Song | None = None
        self.upcoming: list[Song] = []

    def add(self, song: Song | list[Song]) -> None:
        if isinstance(song, list):
            self.upcoming.extend(song)
        else:
            self.upcoming.append(song)
