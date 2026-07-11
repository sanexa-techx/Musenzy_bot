# Telegram Voice Chat Music Bot

Pyrogram + PyTgCalls bot that streams YouTube audio into a Telegram group's voice chat. Commands: `/play`, `/pause`, `/resume`, `/skip`, `/stop`, `/queue`.

## How it works

Two Telegram clients are used together:
- **bot** — a normal BotFather bot that listens for `/play` etc. commands.
- **assistant** — a real user account (via a session string) that joins the voice chat and streams audio. Bot accounts can't join group calls, so this is required.

Audio is streamed directly from yt-dlp's extracted URL (no full download), which keeps disk usage minimal — important on free-tier hosting.

## Local setup

1. Get `API_ID` / `API_HASH` from https://my.telegram.org
2. Create a bot with @BotFather, get `BOT_TOKEN`
3. Generate the assistant session string:
   ```
   pip install pyrogram tgcrypto
   python generate_session.py
   ```
   Log in with the account you want to use as the assistant. That account must already be a member of any group you'll use the bot in.
4. Copy `.env.example` to `.env` and fill in all values.
5. Install deps and run:
   ```
   pip install -r requirements.txt
   python -m bot.main
   ```

## Deploying on JustRunMy.App

1. Push this project to a Git repo (or use the Zip upload option in the JustRunMy dashboard).
2. In the JustRunMy panel: **Add App** → choose **Git push** or **Zip Upload**.
3. Since this project has a `Dockerfile`, JustRunMy will build and run the container automatically — no extra buildpack config needed.
4. In the app's environment variables panel, add: `API_ID`, `API_HASH`, `BOT_TOKEN`, `SESSION_STRING`, `ADMIN_IDS` (optional).
5. This bot doesn't expose an HTTP port (it's a long-running worker, not a web server), so you don't need to configure a public HTTPS port — just make sure the app is set to run as an always-on process/container.
6. Deploy, then check the **logs** tab to confirm "Bot, assistant, and voice call client all started."

## Notes on dependency versions

`pytgcalls`/`ntgcalls` update frequently and versions must match exactly with each other and with pyrogram. The versions pinned in `requirements.txt` are known to work together as of mid-2026. If you hit import errors or connection issues after `pip install`, check the [pytgcalls releases page](https://github.com/pytgcalls/pytgcalls/releases) for the latest compatible pyrogram+ntgcalls combo and update all three pins together.

## Adding features later

- **Admin-only controls**: use `config.ADMIN_IDS` in a filter to restrict `/skip`, `/stop`, etc.
- **Multiple audio sources** (Spotify links, direct files): extend `bot/utils/youtube.py`.
- **Volume control**: `pytgcalls` supports `calls.change_volume_call(chat_id, volume)`.
