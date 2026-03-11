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
import sys
import os
import threading
from flask import Flask, jsonify

from pyrogram import Client
from pyrogram.enums import ParseMode

import environ
from vault import store
from core import herald, conductor, logger
from core import cmds as cmd_module
from relay import engine
from relay.throttle import start_workers
from wire import glyph as G

# --- Flask Health Check Setup ---
app_flask = Flask(__name__)

@app_flask.route('/health', methods=['GET'])
def health_check():
    """Standard health check endpoint for UptimeRobot, Render, or Koyeb."""
    return jsonify({
        "status": "healthy",
        "project": "TeamDev Auto-Forward",
        "version": environ.VERSION
    }), 200

def run_health_server():
    # Use the PORT provided by the hosting service, or default to 8080
    port = int(os.environ.get("PORT", 8080))
    # host 0.0.0.0 is required for external pings to reach the container
    app_flask.run(host='0.0.0.0', port=port)

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("TeamDev")


async def boot():
    # 1. Start the Health Check server in a background thread
    log.info("[ TeamDev ] Starting Health Check server...")
    threading.Thread(target=run_health_server, daemon=True).start()

    # 2. Existing Bot Logic
    log.info("[ TeamDev Auto-Forward ] Connecting to MongoDB...")
    await store.connect()
    log.info("[ TeamDev Auto-Forward ] MongoDB connected.")

    app = Client(
        name="TeamDev_session",
        api_id=environ.API_ID,
        api_hash=environ.API_HASH,
        bot_token=environ.BOT_TOKEN,
    )

    herald.register(app)
    conductor.register(app)
    cmd_module.register(app)
    engine.register(app)

    logger.init(app)

    log.info("[ TeamDev Auto-Forward ] Starting bot...")
    await app.start()
    me = await app.get_me()
    log.info(f"[ TeamDev Auto-Forward ] Running as @{me.username} (id={me.id})")

    await start_workers()
    await logger.validate_log_channel()

    try:
        await app.send_message(
            environ.OWNER_ID,
            f"<b>{G.STAR} TeamDev Auto-Forward v{environ.VERSION} started.</b>\n"
            f"Bot: <code>@{me.username}</code>\n"
            f"Log channel: <code>{environ.LOG_CHANNEL or 'not set'}</code>\n"
            f"Health Port: <code>{os.environ.get('PORT', 8080)}</code>",
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        log.warning(f"[ TeamDev Auto-Forward ] Could not DM owner: {e}")

    log.info("[ TeamDev Auto-Forward ] Live. Ctrl+C to stop.")
    
    # Keep the bot running
    await asyncio.Event().wait()
    await app.stop()


if __name__ == "__main__":
    try:
        asyncio.run(boot())
    except KeyboardInterrupt:
        log.info("[ TeamDev Auto-Forward ] Stopped.")
    except Exception as e:
        log.critical(f"[ TeamDev Auto-Forward ] Fatal: {e}", exc_info=True)
        sys.exit(1)
