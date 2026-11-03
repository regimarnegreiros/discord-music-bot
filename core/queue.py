import random
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

    def shuffle(self) -> None:
        random.shuffle(self.upcoming)

    def move(self, from_idx: int, to_idx: int) -> bool:
        if 0 <= from_idx < len(self.upcoming) and 0 <= to_idx < len(self.upcoming):
            track = self.upcoming.pop(from_idx)
            self.upcoming.insert(to_idx, track)
            return True
        return False

    def remove(self, idx: int) -> Song | None:
        if 0 <= idx < len(self.upcoming):
            return self.upcoming.pop(idx)
        return None

    def clear(self) -> None:
        self.upcoming.clear()
