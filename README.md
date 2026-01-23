# EldricAlarm Bot

## Setup

1. **Intents**: Go to the [Discord Developer Portal](https://discord.com/developers/applications), select your bot, go to **Bot** tab, and enable **Message Content Intent**. (Voice states are usually enabled by default handling but good to check).
2. **Token**: Open `.env.example`, rename it to `.env`, and paste your Bot Token.
3. **FFmpeg**: Ensure `ffmpeg` is installed.
   - If you don't have it, download it from [ffmpeg.org](https://ffmpeg.org/download.html), extract it, and add the `bin` folder to your System PATH.
4. **Alarm File**: Drag your `alarm.wav` or `alarm.mp3` into this folder.

## Running

Double click `run.bat` or type:
```bash
python bot.py
```

## Usage

1. Join a voice channel.
2. Type `/eldricalarm 60` (to listen for 60 seconds).
3. If user `<309480305289330699>` speaks, the bot will play the alarm and pause listening for 20s.
