# Telegram User Comments

A tool for finding and exporting all comments left by a specific Telegram user (or channel) across posts in one or multiple channels. Results are saved to a CSV file.

> **Note:** Only comments that are direct replies to channel posts (in the discussion thread) are counted.

---

## Requirements

- Python 3.14+
- A Telegram account (used to make API requests)

---

## Installation

```bash
pip install -r requirements.txt
```

---

## Setup

### 1. Add channels to scan

Create `channels.txt` and add one channel per line. Both public and private channels are supported. Your account must be a member of each channel.

```
https://t.me/durov
https://t.me/+ABCDEFGHxxxxxxxx
```

| Format | Type |
|---|---|
| `https://t.me/username` | Public channel |
| `https://t.me/+InviteHash` | Private channel |

---

## Usage

Run the script:

```bash
python bot.py
```

You will be prompted for two inputs:

```
Enter TARGET_USER_ID, @username or t.me link:
POSTS_LIMIT:
```

**Target user** – the person or channel whose comments you want to find. Accepted formats:

| Input | Example |
|---|---|
| Numeric ID | `123456789` |
| Username | `@durov` or `durov` |
| Profile link | `https://t.me/durov` |

**Posts limit** – how many of the latest posts in each channel to scan. For example, `100` scans the last 100 posts per channel.

### First run

On first launch, Pyrogram will ask you to authorize your Telegram account (phone number + confirmation code). A session file `account.session` will be created – subsequent runs will not require re-authorization.

---

## Output

After the script finishes, results are saved to:

```
export_<TARGET_USER_ID>.csv
```

### CSV format

```
datetime, channel name, channel username/link, comment text, direct link to comment
```

### Example row

```
10-04-2026 - 14:32:10,Channel Name,@channelusername,"Hello world!",https://t.me/channelusername/105?comment=9871
```

**Media messages** are exported with descriptive labels instead of text:

| Label | Meaning |
|---|---|
| `[Image]` | Photo |
| `[Video]` | Video |
| `[Voice]` | Voice message |
| `[VideoMessage]` | Round video |
| `[Sticker]` | Sticker |
| `[GIF]` | Animated GIF |
| `[Audio]` | Audio file |
| `[Poll]` | Poll |
| `[File: mime/type]` | Document |
| URL | Web page preview link |
| Coordinates link | Geo location |

---

## Project structure

```
├── bot.py           # Entry point – handles user input and launches the scanner
├── comments.py      # Comments class – core logic for scanning and exporting
├── channels.txt     # List of channels to scan (one per line)
├── requirements.txt # Python dependencies
└── account.session  # Pyrogram session file (auto-created on first run)
```

---

## Contributing

Pull requests are welcome.

## License

[MIT](https://github.com/svtcore/telegram-user-comments/blob/main/LICENSE)
