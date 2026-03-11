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

import logging
from pyrogram import Client
from pyrogram.types import Message
from vault import store
from relay.throttle import enqueue

log = logging.getLogger("TeamDev.engine")


def _source_matches(source: str, chat_id: int, username: str | None) -> bool:
    if not source:
        return False

    src = source.strip().lower()

    if src.lstrip("-").isdigit():
        return int(src) == chat_id

    if src.startswith("@"):
        return username is not None and src == f"@{username.lower()}"

    return False


def register(app: Client):

    @app.on_message()
    async def catch_all(client: Client, msg: Message):
        if not msg.chat:
            return

        chat_id  = msg.chat.id
        username = msg.chat.username.lower() if msg.chat.username else None

        try:
            active_pipes = await store.get_active_pipelines()
        except Exception as e:
            log.error(f"[engine] DB error fetching pipelines: {e}")
            return

        for pipe in active_pipes:
            source = pipe.get("source")
            if not source:
                continue
            if _source_matches(source, chat_id, username):
                queued = await enqueue(pipe, client, msg)
                if not queued:
                    log.warning(
                        f"[engine] pipe={pipe['pipe_id']} queue full "
                        f"— msg {msg.id} dropped"
                    )
