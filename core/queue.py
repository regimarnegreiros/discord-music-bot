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

    def next(self) -> Song | None:
        if self.current:
            self.history.append(self.current)
        self.current = self.upcoming.pop(0) if self.upcoming else None
        return self.current

    def previous(self) -> Song | None:
        if not self.history:
            return None
        if self.current:
            self.upcoming.insert(0, self.current)
        self.current = self.history.pop()
        return self.current
