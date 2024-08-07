import datetime
from pyrogram import Client
from pyrogram.raw import functions
import time
import random
from pyrogram.errors import BadRequest, FloodWait
from datetime import datetime
import codecs
import math


class Comments:

    API_ID = None
    API_HASH = None
    TARGET_USER_ID = None
    POSTS_LIMIT = None
    channels = []

    '''
    Load data from .env file
    '''
    def __init__(self, api_id, api_hash, target_user_id, posts_limit):
        self.API_ID = api_id
        self.API_HASH = api_hash
        self.TARGET_USER_ID = target_user_id
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
            file = codecs.open("export_" + str(self.TARGET_USER_ID) + ".csv", "a", encoding='utf-8')
            file.write(data)
            file.close()
        except NameError:
            print(NameError)
    
    '''
    Get data about comments and related with it users
    '''
    def getReplies(self, channel_id, channel_message_id, offset):
        try:
            channel_peer = self.app.resolve_peer(channel_id)
            result = self.app.invoke(
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
            return result
        except NameError:
            print(NameError)

    '''
    Iterate message part, check if comment from target user then concatenate it with other comment data
    Processing only text messages
    '''
    def formatResultText(self, result, channel_link, channel_title, channel_username, channel_message_id, channel_private_status):
        try:
            result_text = ""
            for j in range(0, len(result.messages)):
                found = False
                # convert unix date to str format
                str_date = datetime.fromtimestamp(result.messages[j].date).strftime('%d-%m-%Y - %H:%M:%S')
                #check if message sent from user
                if hasattr(result.messages[j].from_id, 'user_id'):
                    # check if comment from target user
                    if str(self.TARGET_USER_ID) == str(result.messages[j].from_id.user_id):
                        found = True
                #case when message sent from channel
                elif hasattr(result.messages[j].from_id, 'channel_id'):
                    if str(self.TARGET_USER_ID) == str(result.messages[j].from_id.channel_id):
                        found = True
                if (found):
                    if str(result.messages[j].message).strip() != "":
                        #replace \n to avoid crashing formatting on the export file
                        user_message = (result.messages[j].message).replace('\n', '.')
                        #double quotes crashing formatting on the export file so replace it to another type
                        user_message = (result.messages[j].message).replace('"', '`')
                    else:
                        try:
                            #other types of messsages voices, gifs, video
                            if hasattr(result.messages[j].media, 'document'):
                                user_message = str(result.messages[j].media.document.mime_type)
                            else:
                                user_message = "UNKNOWN_TYPE_OF_MESSAGE"
                        except:
                            print("PROBLEM_WITH_RECONGNIZING_NO_TEXT_MESSAGE")
                    if (channel_private_status):
                        result_text = (result_text + str(str_date) + ',' + str(channel_title) + ',' + str(channel_link) + ',' + '"'+str(user_message).strip(
                        ) + '"'+','+'https://t.me/c/' + str(result.messages[j].peer_id.channel_id) + '/' + str(result.messages[j].id) + '?thread=' + str(result.messages[j].reply_to.reply_to_msg_id)).strip() + '\n'
                    else:
                        result_text = (result_text + str(str_date) + ',' + str(channel_title) + ',' + str(channel_username) + ',' + '"'+str(user_message).strip(
                        ) + '"'+','+'https://t.me/' + str(channel_username) + '/' + str(channel_message_id) + '?comment=' + str(result.messages[j].id)).strip() + '\n'
            if result_text.strip() == "":
                return None
            else:
                return result_text
        except NameError:
            return NameError

    '''
    Check channel state private or public
    '''
    def checkPrivateChannel(self, channel_id):
        try:
            chat = self.app.get_chat(channel_id)
            #if channel has username then it's public
            if chat.username:
                return False
            else:
                return True
        except NameError:
            print(NameError)

    '''
    Get channel id based on link
    '''
    def getChannelId(self, channel_link):
        try:
            #private channel case
            if (channel_link.startswith("https://t.me/+")) or channel_link.startswith("http://t.me/+") or channel_link.startswith("t.me/+"):
                chat = self.app.get_chat(channel_link)
            else:
                #public channel, cut only username
                username = channel_link.split("/")[-1]
                chat = self.app.get_chat(username)
            chat_id = chat.id
            return chat_id
        except NameError:
            print(NameError)

    '''
    Main methods call methods for work, get basic data for work, process it and write to file
    '''
    def getComments(self):
        try:
            self.loadChannels()
            self.auth()
            for channel in self.channels:
                channel_general_id = self.getChannelId(channel)
                channel_private_status = self.checkPrivateChannel(channel_general_id)
                target_message_history = list(self.app.get_chat_history(
                    channel_general_id, limit=self.POSTS_LIMIT))
                for i in range(0, len(target_message_history)):
                    try:
                        channel_id = target_message_history[i].sender_chat.id
                        channel_title = target_message_history[i].sender_chat.title
                        channel_username = target_message_history[i].sender_chat.username
                        channel_message_id = target_message_history[i].id
                        if (channel_username == None):
                            channel_username = channel_title
                        print("Processing " + "[" + str(int(i + 1)) + "/" + str(len(target_message_history)) + "] " + str(channel_username) + "/" + str(channel_message_id))
                        # Getting data about comments in post
                        result = self.getReplies(channel_id, channel_message_id, 0)
                        offset = 0
                        # According to GetRelipes method return up to 100 messages per query, 
                        # then run it through loop and increase offset on 100 to get all comments
                        for k in range(0, math.ceil(int(result.count)/100)):
                            result = self.getReplies(channel_id, channel_message_id, offset)
                            offset = offset + 100
                            result_text = self.formatResultText(result, channel, channel_title, channel_username, channel_message_id, channel_private_status)
                            if (result_text != None):
                                self.writeToFile(result_text)
                            time.sleep(2)
                    except BadRequest as e:  # if post deleted
                        time.sleep(0.5)
                        pass
                    except AttributeError as e:  # if no comments under post
                        time.sleep(0.5)
                        pass
                    except IndexError as e:
                        time.sleep(0.5)
                        pass
                    except FloodWait as e:
                        print("Too fast. Sleeping 60 sec")
                        time.sleep(60)
                    except FileNotFoundError as e:
                        pass
                    except NameError as e:
                        print(NameError)
            self.logout()
        except NameError:
            print(NameError)
