# ⚙️ IP Notifier

This is a small script that listens for IP address changes on your machine and sends a Telegram message when it happens.  
It uses Netlink events instead of polling, so it's efficient and stays out of the way. Good for setups like Raspberry Pi where the IP might change and you want to know when it does.

## What It Does

- **Listens for IP changes** using Netlink (via `pyroute2`)
- **Sends a Telegram message** with the new IP address
- **Optionally writes the IP to a file** so you don’t get repeated alerts for the same address
- **Very lightweight** – no loops, no cron jobs, just waits for events
- **Split into three files** so it’s easy to use or adapt just part of it:
  - `listener.py`: watches for IP change events
  - `notifier.py`: sends Telegram messages
  - `writer.py`: handles optional logging

## Configuration

You'll need to create a `.env.ip_notify` file with your Telegram bot details and config path.  
This file is not included in the repo – you’ll have to create it manually.

Example:

```env
# .env.ip_notify
BOT_TOKEN=123456789:ABCDEFyourtelegrambottoken
CHAT_ID=123456789
LAST_IP_FILE=/path/to/last_ip.txt
```

`LAST_IP_FILE` is used to keep track of the last IP sent, so it won’t notify you again if it hasn’t changed.

That’s it. It’s not meant to be a full monitoring suite or anything fancy. Just a tool that solves a specific problem.

## Use Case

I use it to track IP changes on devices with dynamic IPs – mainly a Raspberry Pi running headless.  
It might help someone else, so I’m sharing it.

## Getting Your Telegram Bot Token and Chat ID

1. **Create a bot** using [@BotFather](https://t.me/BotFather):
   - Start a chat with BotFather on Telegram.
   - Send `/newbot` and follow the prompts.
   - It will give you a **bot token** like `123456789:ABCDEF...` – save that for `BOT_TOKEN`.
   - Remember to send at least one message to your new bot for it to be able to send you notications.

2. **Get your chat ID**:
   - Open Telegram and talk to [@userinfobot](https://t.me/userinfobot).
   - It will reply with your **user ID** – use that for `CHAT_ID`.


## Running as a systemd service

You can set this up to run in the background on boot with `systemd`.

Create a service file, for example:

```ini
# /etc/systemd/system/ip-notify.service
[Unit]
Description=IP Notifier
After=network.target

[Service]
ExecStart=/usr/bin/python3 /path/to/your/ip-notify/listener.py
WorkingDirectory=/path/to/your/ip-notify/
Restart=on-failure
User=youruser

[Install]
WantedBy=multi-user.target
```

Then enable and start the service:

```bash
sudo systemctl daemon-reexec
sudo systemctl enable ip-notify.service
sudo systemctl start ip-notify.service
```

Make sure to update the paths and username according to your setup.
