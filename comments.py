import datetime
from os import close
from pyrogram import Client
from pyrogram.raw import functions
import time
import random
from pyrogram.errors import BadRequest, FloodWait
from datetime import datetime
import codecs


class Comments:

    API_ID = None
    API_HASH = None
    TARGET_USER_ID = None
    COMMENTS_LIMIT = None
    POSTS_LIMIT = None
    channels = []

    '''
    Load data from .env file
    '''
    def __init__(self, api_id, api_hash, target_user_id, comments_limit, posts_limit):
        self.API_ID = api_id
        self.API_HASH = api_hash
        self.TARGET_USER_ID = target_user_id
        self.COMMENTS_LIMIT = comments_limit
        self.POSTS_LIMIT = posts_limit

    '''
    Authorize and create account.session file
    '''
    def auth(self):
        try:
            self.app = Client("account", api_id=self.API_ID,
                              api_hash=self.API_HASH)
            self.app.start()
        except NameError:
            print(NameError)
    '''
    Finish session
    '''
    def logout(self):
        try:
            self.app.stop()
        except NameError:
            print(NameError)

    '''
    Load channel names from file channels.txt and put them to array
    '''
    def loadChannels(self):
        try:
            text_file = open("channels.txt", "r")
            lines = text_file.readlines()
            for i in range(0, len(lines)):
                self.channels.append(lines[i].strip())
            text_file.close()
        except NameError:
            print(NameError)

    '''
    Write data in csv row format into file export.csv
    '''
    def writeToFile(self, data):
        try:
            file = codecs.open("export.csv", "a", encoding='utf-8')
            file.write(data)
            file.close()
        except NameError:
            print(NameError)
    
    '''
    Get data about comments and related with it users
    '''
    def getReplies(self, channel_id, channel_message_id):
        try:
            channel_peer = self.app.resolve_peer(channel_id)
            result = self.app.send(
                functions.messages.GetReplies(
                    peer=channel_peer,
                    msg_id=channel_message_id,
                    offset_id=0,
                    offset_date=0,
                    add_offset=0,
                    limit=self.COMMENTS_LIMIT,
                    max_id=9999999,
                    min_id=1,
                    hash=random.randint(100000000, 999999999))
            )
            return result
        except NameError:
            return NameError

    '''
    Iterate message part, check if comment from target user then concatenate it with other comment data
    It skips stickers, images, files. Processing only text
    '''
    def formatResultText(self, result, channel_title, channel_username, channel_message_id):
        try:
            result_text = ""
            for j in range(0, result.count):
                # convert unix date to str format
                str_date = datetime.fromtimestamp(result.messages[j].date).strftime('%Y-%m-%d %H:%M:%S')
                # check if comment from target user
                if self.TARGET_USER_ID == result.messages[j].from_id.user_id:
                    if str(result.messages[j].message).strip() != "":
                        result_text = (result_text + str(str_date) + ',' + str(channel_title) + ',' + str(channel_username) + ',' + '"'+str(result.messages[j].message).strip(
                        ) + '"'+','+'https://t.me/' + str(channel_username) + '/' + str(channel_message_id) + '?comment=' + str(result.messages[j].id)).strip() + '\n'
            return result_text
        except NameError:
            return NameError
    '''
    Main methods call methods for work, get basic data for work, process it and write to file
    '''
    def getComments(self):
        try:
            self.loadChannels()
            self.auth()
            for channel in self.channels:
                target_message_history = self.app.iter_history(
                    channel, limit=self.POSTS_LIMIT)
                for i in range(0, len(target_message_history)):
                    try:
                        channel_id = target_message_history[i].sender_chat.id
                        channel_title = target_message_history[i].sender_chat.title
                        channel_username = target_message_history[i].sender_chat.username
                        channel_message_id = target_message_history[i].message_id
                        print("Processing " + channel_username + "/" + str(channel_message_id))
                        result = self.getReplies(channel_id, channel_message_id)
                        result_text = self.formatResultText(result, channel_title, channel_username, channel_message_id)
                        self.writeToFile(result_text)
                        time.sleep(1.2)
                    except BadRequest as e:  # if post deleted
                        pass
                    except AttributeError as e:  # if no comments under post
                        pass
                    except IndexError as e:
                        pass
                    except FloodWait as e:
                        print("Too fast. Sleeping 60 sec")
                        time.sleep(60)
                    except NameError as e:
                        print(NameError)
            self.logout()
        except NameError:
            print(NameError)
