# Telegram User Comments

Get all user comments under posts (discussion) in certain channel(s) and export in file

Note: Count only comments whose defined like reply to post

## Installation
```
pip install -r requirements.txt
```
## Setup
### 1. Go to [https://my.telegram.org/apps](https://my.telegram.org/apps "https://my.telegram.org/apps"). Create application and get credential data API_ID and API_HASH
### 2. Rename file **.env.example** to **.env**
### 3. Open **.env** file and set parameters

  ```API_ID``` - Telegram app credential from step 1

  ```API_HASH``` - Telegram app credential from step 1

  ``TARGET_USER_ID`` - Telegram user id whose comments need to be found 

  ```POSTS_LIMIT``` - Count of posts which will process. The number define the last **N** posts

### 4. Open **channels.txt** and add channel(s) to process 

  Only channel username (ex. https:/t.me/durov, username is **durov**)

  ```
  channel_username_1
  channel_username_2
  channel_username_3
  ```

## Run

```
python bot.py
```

After start you should authorize in telegram account and script will create file **account.session** for further work 

## Export

After script end working all found data will be export in file **export.csv**

Data format

```
datetime, channel name, channel username, comment, link
```

## Contributing
Pull requests are welcome.

## License
[MIT](https://github.com/svtcore/telegram-user-comments/blob/main/LICENSE "MIT")
