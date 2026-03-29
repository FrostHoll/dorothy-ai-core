from enum import Enum


class VoiceSessionState(Enum):
    IDLE = 0
    COLLECTING = 1
    PROCESSING = 2
    GENERATING = 3
    DONE = 4
    EXPIRED = 5