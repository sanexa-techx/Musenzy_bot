from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream, Update
from pytgcalls.exceptions import NoActiveGroupCall

from ..utils.queue import queue_manager, Track
from ..utils.youtube import resolve_track


def _controls_keyboard(paused: bool) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("▶️ Resume" if paused else "⏸ Pause", callback_data="ctl_pause_resume"),
                InlineKeyboardButton("⏭ Skip", callback_data="ctl_skip"),
                InlineKeyboardButton("⏹ Stop", callback_data="ctl_stop"),
            ]
        ]
    )


def register_music_handlers(bot: Client, calls: PyTgCalls):

    async def _play_next(chat_id: int, announce_chat=None):
        next_track = queue_manager.pop_next(chat_id)
        if next_track is None:
            queue_manager.set_now_playing(chat_id, None)
            await calls.leave_call(chat_id)
            return
        queue_manager.set_now_playing(chat_id, next_track)
        queue_manager.set_paused(chat_id, False)
        await calls.play(chat_id, MediaStream(next_track.stream_url))
        if announce_chat is not None:
            await announce_chat.send_message(
                f"▶️ Now playing: **{next_track.title}**",
                reply_markup=_controls_keyboard(paused=False),
            )

    @bot.on_message(filters.command("play") & filters.group)
    async def play_cmd(client: Client, message: Message):
        if len(message.command) < 2:
            await message.reply_text("Usage: /play <song name or YouTube URL>")
            return

        query = message.text.split(None, 1)[1]
        status = await message.reply_text(f"🔎 Searching: {query}")

        try:
            info = await resolve_track(query)
        except Exception as e:
            await status.edit_text(f"❌ Couldn't find that track: {e}")
            return

        track = Track(
            title=info["title"],
            url=info["webpage_url"],
            stream_url=info["stream_url"],
            duration=info["duration"],
            requested_by=message.from_user.mention if message.from_user else "someone",
        )

        chat_id = message.chat.id
        currently_playing = queue_manager.now_playing(chat_id)

        if currently_playing is None:
            queue_manager.set_now_playing(chat_id, track)
            try:
                await calls.play(chat_id, MediaStream(track.stream_url))
            except NoActiveGroupCall:
                await status.edit_text(
                    "❌ No active voice chat found. Start the group voice chat first."
                )
                queue_manager.set_now_playing(chat_id, None)
                return
            await status.edit_text(
                f"▶️ Now playing: **{track.title}**",
                reply_markup=_controls_keyboard(paused=False),
            )
        else:
            queue_manager.add(chat_id, track)
            position = len(queue_manager.get_queue(chat_id))
            await status.edit_text(f"✅ Queued at position {position}: **{track.title}**")

    @bot.on_message(filters.command("skip") & filters.group)
    async def skip_cmd(client: Client, message: Message):
        chat_id = message.chat.id
        if queue_manager.now_playing(chat_id) is None:
            await message.reply_text("Nothing is playing right now.")
            return
        await message.reply_text("⏭ Skipped.")
        await _play_next(chat_id)

    @bot.on_message(filters.command("pause") & filters.group)
    async def pause_cmd(client: Client, message: Message):
        chat_id = message.chat.id
        await calls.pause(chat_id)
        queue_manager.set_paused(chat_id, True)
        await message.reply_text("⏸ Paused.")

    @bot.on_message(filters.command("resume") & filters.group)
    async def resume_cmd(client: Client, message: Message):
        chat_id = message.chat.id
        await calls.resume(chat_id)
        queue_manager.set_paused(chat_id, False)
        await message.reply_text("▶️ Resumed.")

    @bot.on_message(filters.command("stop") & filters.group)
    async def stop_cmd(client: Client, message: Message):
        chat_id = message.chat.id
        queue_manager.clear(chat_id)
        try:
            await calls.leave_call(chat_id)
        except Exception:
            pass
        await message.reply_text("⏹ Stopped and cleared the queue.")

    @bot.on_message(filters.command("queue") & filters.group)
    async def queue_cmd(client: Client, message: Message):
        chat_id = message.chat.id
        current = queue_manager.now_playing(chat_id)
        upcoming = list(queue_manager.get_queue(chat_id))

        if not current:
            await message.reply_text("Queue is empty.")
            return

        lines = [f"🎵 **Now playing:** {current.title}"]
        if upcoming:
            lines.append("\n**Up next:**")
            for i, t in enumerate(upcoming, 1):
                lines.append(f"{i}. {t.title}")
        await message.reply_text("\n".join(lines))

    # --- Inline button callbacks (same controls as the slash commands) ---

    @bot.on_callback_query(filters.regex("^ctl_pause_resume$"))
    async def ctl_pause_resume(client: Client, callback: CallbackQuery):
        chat_id = callback.message.chat.id
        if queue_manager.now_playing(chat_id) is None:
            await callback.answer("Nothing is playing.", show_alert=True)
            return

        paused = queue_manager.is_paused(chat_id)
        if paused:
            await calls.resume(chat_id)
            queue_manager.set_paused(chat_id, False)
            await callback.answer("Resumed")
        else:
            await calls.pause(chat_id)
            queue_manager.set_paused(chat_id, True)
            await callback.answer("Paused")

        await callback.message.edit_reply_markup(
            _controls_keyboard(paused=not paused)
        )

    @bot.on_callback_query(filters.regex("^ctl_skip$"))
    async def ctl_skip(client: Client, callback: CallbackQuery):
        chat_id = callback.message.chat.id
        if queue_manager.now_playing(chat_id) is None:
            await callback.answer("Nothing is playing.", show_alert=True)
            return
        await callback.answer("Skipped")
        await _play_next(chat_id, announce_chat=callback.message.chat)

    @bot.on_callback_query(filters.regex("^ctl_stop$"))
    async def ctl_stop(client: Client, callback: CallbackQuery):
        chat_id = callback.message.chat.id
        queue_manager.clear(chat_id)
        try:
            await calls.leave_call(chat_id)
        except Exception:
            pass
        await callback.answer("Stopped")
        await callback.message.edit_text("⏹ Stopped and cleared the queue.")

    # Auto-advance queue when a track finishes
    @calls.on_update()
    async def on_stream_end(client: PyTgCalls, update: Update):
        if update.__class__.__name__ == "StreamEnded":
            chat = await bot.get_chat(update.chat_id)
            await _play_next(update.chat_id, announce_chat=chat)
