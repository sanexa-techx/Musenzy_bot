import asyncio
import logging

from pyrogram import Client
from pytgcalls import PyTgCalls

from . import config
from .handlers.music import register_music_handlers
from .handlers.general import register_general_handlers

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("music-bot")

# The "bot" receives commands from users (BotFather token).
bot = Client(
    "music-bot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
)

# The "assistant" is a regular user account that actually joins the
# group voice chat and streams audio. Group voice chats can only be
# joined by user accounts, not bot accounts — this is why two clients
# are needed.
assistant = Client(
    "assistant",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    session_string=config.SESSION_STRING,
)

calls = PyTgCalls(assistant)

register_music_handlers(bot, calls)
register_general_handlers(bot)


async def main():
    await bot.start()
    await assistant.start()
    await calls.start()
    log.info("Bot, assistant, and voice call client all started.")
    await idle()


async def idle():
    stop_event = asyncio.Event()
    await stop_event.wait()


if __name__ == "__main__":
    asyncio.run(main())
