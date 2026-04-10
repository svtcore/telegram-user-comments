import math
import random
import time
from datetime import datetime

from pyrogram import Client
from pyrogram.errors import BadRequest, FloodWait
from pyrogram.raw import functions


class Comments:
    """Parses user comments under Telegram channel posts and exports to CSV"""

    def __init__(self, api_id, api_hash, target_user_id, posts_limit):
        """Initialize with Telegram API credentials and search parameters"""
        self._api_id = api_id
        self._api_hash = api_hash
        self._target_user_id = target_user_id
        self._posts_limit = posts_limit
        self._channels = []
        self._app = None

    def _auth(self):
        """Authorize and create account.session file"""
        self._app = Client("account", api_id=self._api_id,
                           api_hash=self._api_hash)
        self._app.start()

    def _logout(self):
        """Finish session"""
        if self._app:
            self._app.stop()

    def _load_channels(self):
        """Load channel links from channels.txt into a list"""
        try:
            with open("channels.txt", "r") as f:
                self._channels = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            raise FileNotFoundError(
                "channels.txt not found. Create the file and add at least one channel link"
            )

    def _write_to_file(self, data):
        """Append CSV-formatted data to an export file"""
        with open(f"export_{self._target_user_id}.csv", "a", encoding="utf-8") as f:
            f.write(data)

    def _get_media_info(self, message):
        """Detect media type and return a label or link"""
        media = message.media
        if media is None:
            return "[Empty]"

        type_name = type(media).__name__

        if type_name == "MessageMediaPhoto":
            return "[Image]"

        if type_name == "MessageMediaDocument":
            doc = media.document
            attrs = {type(a).__name__: a for a in getattr(doc, 'attributes', [])}
            if 'DocumentAttributeSticker' in attrs:
                return "[Sticker]"
            if 'DocumentAttributeAnimated' in attrs:
                return "[GIF]"
            if 'DocumentAttributeAudio' in attrs:
                audio = attrs['DocumentAttributeAudio']
                return "[Voice]" if getattr(audio, 'voice', False) else "[Audio]"
            if 'DocumentAttributeVideo' in attrs:
                video = attrs['DocumentAttributeVideo']
                return "[VideoMessage]" if getattr(video, 'round_message', False) else "[Video]"
            mime = getattr(doc, 'mime_type', '')
            if mime.startswith('image/'):
                return "[Image]"
            return f"[File: {mime}]" if mime else "[Document]"

        if type_name == "MessageMediaWebPage":
            webpage = media.webpage
            url = getattr(webpage, 'url', None)
            return url if url else "[WebPage]"

        if type_name == "MessageMediaGeo":
            geo = media.geo
            if hasattr(geo, 'lat') and hasattr(geo, 'long'):
                return f"https://maps.google.com/?q={geo.lat},{geo.long}"
            return "[Location]"

        if type_name == "MessageMediaGeoLive":
            return "[LiveLocation]"

        if type_name == "MessageMediaContact":
            return f"[Contact: {media.first_name} {media.last_name}]"

        if type_name == "MessageMediaPoll":
            return "[Poll]"

        if type_name == "MessageMediaDice":
            return f"[Dice: {media.emoticon}]"

        if type_name == "MessageMediaUnsupported":
            return "[Unsupported]"

        # Fallback for types that may not be in this Pyrogram version
        known_types = {
            "MessageMediaStory": "[Story]",
            "MessageMediaGiveaway": "[Giveaway]",
            "MessageMediaGiveawayResults": "[GiveawayResults]",
            "MessageMediaInvoice": "[Invoice]",
        }
        return known_types.get(type_name, f"[{type_name}]")

    def _get_replies(self, channel_id, channel_message_id, offset):
        """Fetch comment replies for a specific channel post"""
        channel_peer = self._app.resolve_peer(channel_id)
        return self._app.invoke(
            functions.messages.GetReplies(
                peer=channel_peer,
                msg_id=channel_message_id,
                offset_id=0,
                offset_date=0,
                add_offset=offset,
                limit=100,
                max_id=9999999,
                min_id=1,
                hash=random.randint(100000000, 999999999))
        )

    def _format_result_text(self, result, channel_link, channel_title,
                            channel_username, channel_message_id, channel_private_status):
        """Filter comments from the target user and format them as CSV rows"""
        result_text = ""
        for msg in result.messages:
            found = False
            # Convert unix date to string format
            str_date = datetime.fromtimestamp(msg.date).strftime('%d-%m-%Y - %H:%M:%S')
            # Check if message sent from user
            if hasattr(msg.from_id, 'user_id'):
                if str(self._target_user_id) == str(msg.from_id.user_id):
                    found = True
            # Case when message sent from channel or community
            elif hasattr(msg.from_id, 'channel_id'):
                # Raw API always uses positive channel_id, normalize target too
                if str(abs(self._target_user_id)) == str(msg.from_id.channel_id):
                    found = True

            if found:
                if str(msg.message).strip():
                    user_message = msg.message
                    user_message = user_message.replace('\n', '\\n')
                    user_message = user_message.replace('\r', '\\r')
                    user_message = user_message.replace('\t', '\\t')
                    user_message = user_message.replace('"', '""')
                else:
                    try:
                        user_message = self._get_media_info(msg)
                    except Exception as e:
                        user_message = "[UNKNOWN]"
                        print(f"Could not detect media type: {e}")

                if channel_private_status:
                    link = (f"https://t.me/c/{msg.peer_id.channel_id}"
                            f"/{msg.id}?thread={msg.reply_to.reply_to_msg_id}")
                    result_text += (f"{str_date},{channel_title},{channel_link},"
                                    f'"{user_message.strip()}",{link}\n')
                else:
                    link = (f"https://t.me/{channel_username}"
                            f"/{channel_message_id}?comment={msg.id}")
                    result_text += (f"{str_date},{channel_title},{channel_username},"
                                    f'"{user_message.strip()}",{link}\n')

        return result_text if result_text.strip() else None

    def _check_private_channel(self, channel_id):
        """Check whether a channel is private or public."""
        chat = self._app.get_chat(channel_id)
        # If channel has a username then it's public
        return not bool(chat.username)

    def _get_channel_id(self, channel_link):
        """Resolve a channel link to its numeric ID"""
        # Private channel case
        if any(channel_link.startswith(prefix) for prefix in
               ("https://t.me/+", "http://t.me/+", "t.me/+")):
            chat = self._app.get_chat(channel_link)
        else:
            # Public channel, extract only the username
            username = channel_link.split("/")[-1]
            chat = self._app.get_chat(username)
        return chat.id

    def get_comments(self):
        """Main entry point: load channels, fetch comments, and export to file"""
        self._load_channels()
        self._auth()
        try:
            for channel in self._channels:
                channel_general_id = self._get_channel_id(channel)
                channel_private_status = self._check_private_channel(channel_general_id)
                target_message_history = list(self._app.get_chat_history(
                    channel_general_id, limit=self._posts_limit))

                for i, post in enumerate(target_message_history):
                    try:
                        channel_id = post.sender_chat.id
                        channel_title = post.sender_chat.title
                        channel_username = post.sender_chat.username or channel_title
                        channel_message_id = post.id

                        print(f"Processing [{i + 1}/{len(target_message_history)}] "
                              f"{channel_username}/{channel_message_id}")

                        # GetReplies returns up to 100 messages per query,
                        # loop with increasing offset to get all comments
                        result = self._get_replies(channel_id, channel_message_id, 0)
                        offset = 0
                        for _ in range(math.ceil(int(result.count) / 100)):
                            result = self._get_replies(channel_id, channel_message_id, offset)
                            offset += 100
                            result_text = self._format_result_text(
                                result, channel, channel_title, channel_username,
                                channel_message_id, channel_private_status)
                            if result_text is not None:
                                self._write_to_file(result_text)
                            time.sleep(2)
                    except BadRequest:
                        time.sleep(0.5)
                    except AttributeError:
                        time.sleep(0.5)
                    except IndexError:
                        time.sleep(0.5)
                    except FloodWait:
                        print("Too fast. Sleeping 60 sec")
                        time.sleep(60)
                    except FileNotFoundError:
                        pass
        finally:
            self._logout()
