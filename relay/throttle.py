"""
                      [TeamDev](https://t.me/team_x_og)
          
          Project Id -> 30.
          Project Name -> TeamDev Auto-Forward
          Project Age -> 1Month+ (Updated On 11/03/2026)
          Project Idea By -> @MR_ARMAN_08
          Project Dev -> @MR_ARMAN_08
          Powered By -> @Team_X_Og ( On Telegram )
          Updates -> @CrimeZone_Update ( On telegram )
    
    Setup Guides -> Read > README.md
    
          This Script Part Off https://t.me/Team_X_Og's Team.
          Copyright ©️ 2026 TeamDev | @Team_X_Og

    Compatible In BotApi 9.5 Fully
"""

import asyncio
import time
import logging
from collections import defaultdict
from pyrogram import Client
from pyrogram.types import Message

import environ

log = logging.getLogger("TeamDev.throttle")

_flood_until: float = 0.0


def set_flood_wait(seconds: int):
    global _flood_until
    _flood_until = time.monotonic() + seconds + 2
    log.warning(f"[throttle] FloodWait — all queues paused for {seconds}s")


async def wait_flood():
    wait = _flood_until - time.monotonic()
    if wait > 0:
        log.info(f"[throttle] Waiting {wait:.1f}s for FloodWait to clear...")
        await asyncio.sleep(wait)


QUEUE_MAX = 200

class _TokenBucket:
    def __init__(self, rate: float):
        self.rate     = rate
        self.tokens   = rate
        self._last    = time.monotonic()

    def consume(self) -> float:
        now    = time.monotonic()
        delta  = now - self._last
        self._last = now
        self.tokens = min(self.rate, self.tokens + delta * self.rate)
        if self.tokens >= 1.0:
            self.tokens -= 1.0
            return 0.0
        wait = (1.0 - self.tokens) / self.rate
        self.tokens = 0
        return wait


_queues:  dict[int, asyncio.Queue]  = {}
_buckets: dict[int, _TokenBucket]   = {}


def get_queue(pipe_id: int, rate_per_min: int = None) -> asyncio.Queue:
    if pipe_id not in _queues:
        _queues[pipe_id]  = asyncio.Queue(maxsize=QUEUE_MAX)
        rpm = rate_per_min or environ.RATE_LIMIT
        _buckets[pipe_id] = _TokenBucket(rpm / 60.0)
    return _queues[pipe_id]


def drop_queue(pipe_id: int):
    _queues.pop(pipe_id, None)
    _buckets.pop(pipe_id, None)


async def enqueue(pipe: dict, client: Client, msg: Message) -> bool:
    pid   = pipe["pipe_id"]
    rpm   = pipe.get("rate_limit", environ.RATE_LIMIT)
    queue = get_queue(pid, rpm)

    if queue.full():
        log.debug(f"[throttle] pipe={pid} queue full — dropping msg {msg.id}")
        return False

    await queue.put((client, msg, pipe))
    return True

async def _worker(worker_id: int):
    from relay.shifter import relay_message

    log.info(f"[worker-{worker_id}] started")

    while True:
        dispatched = False

        for pid, queue in list(_queues.items()):
            if queue.empty():
                continue

            try:
                client, msg, pipe = queue.get_nowait()
            except asyncio.QueueEmpty:
                continue

            dispatched = True

            await wait_flood()

            bucket = _buckets.get(pid)
            if bucket:
                wait = bucket.consume()
                if wait > 0:
                    await asyncio.sleep(wait)

            delay = float(pipe.get("delay", 1.5))
            if delay > 0:
                await asyncio.sleep(delay)

            try:
                await relay_message(client, msg, pipe)
            except Exception as e:
                log.error(f"[worker-{worker_id}] pipe={pid} relay error: {e}")

            queue.task_done()

        if not dispatched:
            await asyncio.sleep(0.05)


async def start_workers():
    for i in range(environ.WORKERS):
        asyncio.create_task(_worker(i))
    log.info(f"[throttle] {environ.WORKERS} workers started")
