import os
from dotenv import load_dotenv
from comments import Comments

load_dotenv()

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
TARGET_USER_ID = int(os.environ.get("TARGET_USER_ID"))
COMMENTS_LIMIT = int(os.environ.get("COMMENTS_LIMIT"))
POSTS_LIMIT = int(os.environ.get("POSTS_LIMIT"))

com_object = Comments(API_ID, API_HASH, TARGET_USER_ID, COMMENTS_LIMIT, POSTS_LIMIT)
com_object.getComments()