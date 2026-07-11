import asyncio
import yt_dlp

_YDL_OPTS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "no_warnings": True,
    "default_search": "ytsearch",
    "source_address": "0.0.0.0",
}


def _extract(query: str) -> dict:
    with yt_dlp.YoutubeDL(_YDL_OPTS) as ydl:
        info = ydl.extract_info(query, download=False)
        if "entries" in info:
            info = info["entries"][0]
        return info


async def resolve_track(query: str) -> dict:
    """Runs the blocking yt-dlp extraction in a thread so it doesn't block the event loop.

    Returns dict with: title, webpage_url, stream_url, duration
    """
    loop = asyncio.get_event_loop()
    info = await loop.run_in_executor(None, _extract, query)
    return {
        "title": info.get("title", "Unknown"),
        "webpage_url": info.get("webpage_url", query),
        "stream_url": info["url"],
        "duration": info.get("duration", 0),
    }
