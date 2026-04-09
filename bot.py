import asyncio

asyncio.set_event_loop(asyncio.new_event_loop())

from comments import Comments

# Public credentials from Telegram Desktop (open source)
API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"


def resolve_target_user(user_input):
    """Resolve a username or t.me link to a numeric Telegram user/channel ID"""
    # Extract username from t.me link
    if "t.me/" in user_input:
        user_input = user_input.split("t.me/")[-1].split("/")[0].split("?")[0]

    # If numeric ID provided, return directly
    if user_input.lstrip("-").isdigit():
        return int(user_input)

    # Resolve username via Pyrogram
    from pyrogram import Client
    from pyrogram.raw.types import InputPeerUser, InputPeerChannel, InputPeerChat

    username = user_input.lstrip("@")
    app = Client("account", api_id=API_ID, api_hash=API_HASH)
    app.start()
    try:
        peer = app.resolve_peer(username)
        if isinstance(peer, InputPeerUser):
            target_id = peer.user_id
            print(f"User resolved (ID: {target_id})")
        elif isinstance(peer, InputPeerChannel):
            target_id = peer.channel_id
            print(f"Channel/community resolved (ID: {target_id})")
        elif isinstance(peer, InputPeerChat):
            target_id = peer.chat_id
            print(f"Group resolved (ID: {target_id})")
        else:
            raise ValueError(f"Unknown peer type: {type(peer)}")
    finally:
        app.stop()

    return target_id


def main():
    target_user_input = input("Enter TARGET_USER_ID, @username or t.me link: ").strip()
    posts_limit = int(input("POSTS_LIMIT: "))

    target_user_id = resolve_target_user(target_user_input)

    comments = Comments(API_ID, API_HASH, target_user_id, posts_limit)
    try:
        comments.get_comments()
    except FileNotFoundError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()