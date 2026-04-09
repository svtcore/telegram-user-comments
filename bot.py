import asyncio
import json
import os

asyncio.set_event_loop(asyncio.new_event_loop())

from comments import Comments

# Public credentials from Telegram Desktop (open source)
API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"

TARGET_USER_INPUT = input("Enter TARGET_USER_ID or @username: ").strip()
POSTS_LIMIT = int(input("POSTS_LIMIT: "))

# If username provided - get user_id via Pyrogram
if not TARGET_USER_INPUT.lstrip("-").isdigit():
    from pyrogram import Client
    username = TARGET_USER_INPUT.lstrip("@")
    _tmp = Client("account", api_id=API_ID, api_hash=API_HASH)
    _tmp.start()
    user = _tmp.get_users(username)
    TARGET_USER_ID = user.id
    _tmp.stop()
    print(f"User found: {user.first_name} (ID: {TARGET_USER_ID})")
else:
    TARGET_USER_ID = int(TARGET_USER_INPUT)

com_object = Comments(API_ID, API_HASH, TARGET_USER_ID, POSTS_LIMIT)
com_object.getComments()