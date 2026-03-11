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
import logging
from pyrogram.errors import (
    FloodWait,
    SlowmodeWait,
    NetworkMigrate,
    PhoneMigrate,
    FileMigrate,
    ChatAdminRequired,
    ChatWriteForbidden,
    UserBannedInChannel,
    PeerIdInvalid,
    ChannelPrivate,
    ChannelInvalid,
    MessageNotModified,
    RPCError,
)
from relay.throttle import set_flood_wait

try:
    from pyrogram.errors import ChatForwardsRestricted as _ChatFwdErr
except ImportError:
    try:
        from pyrogram.errors import ChatForwardingNotAllowed as _ChatFwdErr
    except ImportError:
        _ChatFwdErr = None

log = logging.getLogger("TeamDev.errors")


class ForwardResult:
    OK       = "ok"
    RETRY    = "retry"
    SKIP     = "skip"
    PERM_ERR = "perm_error"

def _is_fwd_restricted(exc: Exception) -> bool:
    return _ChatFwdErr is not None and isinstance(exc, _ChatFwdErr)


def classify(exc: Exception) -> str:
    if isinstance(exc, FloodWait):
        return ForwardResult.RETRY
    if isinstance(exc, SlowmodeWait):
        return ForwardResult.RETRY
    if isinstance(exc, (NetworkMigrate, PhoneMigrate, FileMigrate)):
        return ForwardResult.RETRY
    if _is_fwd_restricted(exc) or isinstance(exc, (
        ChatWriteForbidden, ChatAdminRequired, UserBannedInChannel,
        PeerIdInvalid, ChannelPrivate, ChannelInvalid,
    )):
        return ForwardResult.PERM_ERR
    if isinstance(exc, MessageNotModified):
        return ForwardResult.SKIP
    return ForwardResult.SKIP


async def handle_and_retry(coro_factory, max_retries: int = 3) -> str:
    attempt = 0
    while attempt <= max_retries:
        try:
            await coro_factory()
            return ForwardResult.OK

        except FloodWait as e:
            log.warning(f"[errors] FloodWait {e.value}s on attempt {attempt+1}")
            set_flood_wait(e.value)
            await asyncio.sleep(e.value + 2)
            attempt += 1

        except SlowmodeWait as e:
            log.warning(f"[errors] SlowmodeWait {e.value}s")
            await asyncio.sleep(e.value + 1)
            attempt += 1

        except (NetworkMigrate, PhoneMigrate, FileMigrate) as e:
            log.warning(f"[errors] MigrateError — retry {attempt+1}: {e}")
            await asyncio.sleep(2 ** attempt)
            attempt += 1

        except (ChatWriteForbidden, ChatAdminRequired, UserBannedInChannel,
                PeerIdInvalid, ChannelPrivate, ChannelInvalid) as e:
            log.error(f"[errors] Permanent target error: {type(e).__name__}: {e}")
            return ForwardResult.PERM_ERR

        except RPCError as e:
            if _is_fwd_restricted(e):
                log.error(f"[errors] Forwarding restricted: {e}")
                return ForwardResult.PERM_ERR
            log.error(f"[errors] RPCError attempt {attempt+1}: {e}")
            await asyncio.sleep(2 ** attempt)
            attempt += 1

        except Exception as e:
            log.error(f"[errors] Unexpected error attempt {attempt+1}: {type(e).__name__}: {e}")
            await asyncio.sleep(1)
            attempt += 1

    log.error(f"[errors] Max retries ({max_retries}) exceeded — skipping")
    return ForwardResult.SKIP
