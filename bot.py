import asyncio
import json
import os

asyncio.set_event_loop(asyncio.new_event_loop())

from comments import Comments

# Public credentials from Telegram Desktop (open source)
API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"

TARGET_USER_INPUT = input("Enter TARGET_USER_ID, @username or t.me link: ").strip()
POSTS_LIMIT = int(input("POSTS_LIMIT: "))

# Extract username from t.me link
if "t.me/" in TARGET_USER_INPUT:
    TARGET_USER_INPUT = TARGET_USER_INPUT.split("t.me/")[-1].split("/")[0].split("?")[0]

# If username provided - resolve via Pyrogram
if not TARGET_USER_INPUT.lstrip("-").isdigit():
    from pyrogram import Client
    from pyrogram.raw.types import InputPeerUser, InputPeerChannel, InputPeerChat
    username = TARGET_USER_INPUT.lstrip("@")
    _tmp = Client("account", api_id=API_ID, api_hash=API_HASH)
    _tmp.start()
    peer = _tmp.resolve_peer(username)
    if isinstance(peer, InputPeerUser):
        TARGET_USER_ID = peer.user_id
        print(f"User resolved (ID: {TARGET_USER_ID})")
    elif isinstance(peer, InputPeerChannel):
        TARGET_USER_ID = peer.channel_id
        print(f"Channel/community resolved (ID: {TARGET_USER_ID})")
    elif isinstance(peer, InputPeerChat):
        TARGET_USER_ID = peer.chat_id
        print(f"Group resolved (ID: {TARGET_USER_ID})")
    else:
        raise ValueError(f"Unknown peer type: {type(peer)}")
    _tmp.stop()
else:
    TARGET_USER_ID = int(TARGET_USER_INPUT)

com_object = Comments(API_ID, API_HASH, TARGET_USER_ID, POSTS_LIMIT)
com_object.getComments()