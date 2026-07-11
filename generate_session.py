"""
Run this ONCE locally (not on the server) to generate SESSION_STRING.

    python generate_session.py

It will ask for your phone number and login code, then print a session
string. Paste that into your .env as SESSION_STRING.

IMPORTANT: This must be a real Telegram user account (not a bot), and
that account must already be a member of any group where you want
music playback.
"""
from pyrogram import Client

API_ID = int(input("API_ID: "))
API_HASH = input("API_HASH: ").strip()

with Client("assistant_session_gen", api_id=API_ID, api_hash=API_HASH, in_memory=True) as app:
    print("\nYour SESSION_STRING (copy this into .env):\n")
    print(app.export_session_string())
