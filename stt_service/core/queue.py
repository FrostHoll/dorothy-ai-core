import asyncio

_queue: asyncio.Queue = asyncio.Queue()

def get_queue() -> asyncio.Queue:
    return _queue