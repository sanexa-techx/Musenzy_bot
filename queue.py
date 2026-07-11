from collections import deque
from dataclasses import dataclass


@dataclass
class Track:
    title: str
    url: str
    stream_url: str
    duration: int
    requested_by: str


class ChatQueue:
    """Holds the music queue + playback state for a single chat."""

    def __init__(self):
        self._queues: dict[int, deque[Track]] = {}
        self._now_playing: dict[int, Track | None] = {}
        self._paused: dict[int, bool] = {}

    def get_queue(self, chat_id: int) -> deque[Track]:
        return self._queues.setdefault(chat_id, deque())

    def add(self, chat_id: int, track: Track):
        self.get_queue(chat_id).append(track)

    def pop_next(self, chat_id: int) -> Track | None:
        q = self.get_queue(chat_id)
        return q.popleft() if q else None

    def clear(self, chat_id: int):
        self._queues.pop(chat_id, None)
        self._now_playing.pop(chat_id, None)
        self._paused.pop(chat_id, None)

    def set_now_playing(self, chat_id: int, track: Track | None):
        self._now_playing[chat_id] = track

    def now_playing(self, chat_id: int) -> Track | None:
        return self._now_playing.get(chat_id)

    def set_paused(self, chat_id: int, paused: bool):
        self._paused[chat_id] = paused

    def is_paused(self, chat_id: int) -> bool:
        return self._paused.get(chat_id, False)


queue_manager = ChatQueue()
