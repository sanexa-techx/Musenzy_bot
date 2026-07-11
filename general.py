from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)


def register_general_handlers(bot: Client):

    @bot.on_message(filters.command("start") & filters.private)
    async def start_cmd(client: Client, message: Message):
        me = await client.get_me()
        text = (
            f"👋 Hi {message.from_user.first_name}!\n\n"
            "I play music in Telegram group voice chats.\n\n"
            "Add me to a group, start the group's voice chat, then use "
            "/play <song name> in that group."
        )
        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "➕ Add me to a group",
                        url=f"https://t.me/{me.username}?startgroup=true",
                    )
                ],
                [InlineKeyboardButton("📖 Commands", callback_data="show_help")],
            ]
        )
        await message.reply_text(text, reply_markup=buttons)

    @bot.on_message(filters.command("help"))
    async def help_cmd(client: Client, message: Message):
        await message.reply_text(_help_text())

    @bot.on_message(filters.command("play") & filters.private)
    async def play_in_private(client: Client, message: Message):
        await message.reply_text(
            "🎵 Music only plays in group voice chats.\n"
            "Add me to a group and use /play there."
        )

    @bot.on_callback_query(filters.regex("^show_help$"))
    async def show_help_cb(client: Client, callback: CallbackQuery):
        await callback.answer()
        await callback.message.edit_text(_help_text())


def _help_text() -> str:
    return (
        "**Commands (use inside a group with an active voice chat):**\n\n"
        "/play <song name or link> — play or queue a track\n"
        "/pause — pause playback\n"
        "/resume — resume playback\n"
        "/skip — skip to the next track\n"
        "/stop — stop and clear the queue\n"
        "/queue — show what's playing and up next\n\n"
        "You can also just tap the buttons under the \"Now playing\" message."
    )
