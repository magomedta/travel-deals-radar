import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Settings
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
raw_channel = os.getenv("TELEGRAM_CHANNEL_ID", "").strip()

# Auto-clean Telegram channel handle (e.g. https://t.me/skidki_biletyi -> @skidki_biletyi)
if raw_channel.startswith("https://t.me/"):
    raw_channel = "@" + raw_channel.replace("https://t.me/", "").strip("/ ")
elif raw_channel and not raw_channel.startswith("@") and not raw_channel.startswith("-100"):
    raw_channel = "@" + raw_channel

TELEGRAM_CHANNEL_ID = raw_channel

# Affiliate Monetization Markers (Travelpayouts / Aviasales / Ostrovok)
# Register free at travelpayouts.com to get your personal marker and earn 1.5% - 5% on bookings
TRAVELPAYOUTS_MARKER = os.getenv("TRAVELPAYOUTS_MARKER", "521190")
TRAVELPAYOUTS_TOKEN = os.getenv("TRAVELPAYOUTS_TOKEN", "")

# Scanner Settings
SCAN_INTERVAL_SECONDS = int(os.getenv("SCAN_INTERVAL_SECONDS", "180")) # 3 minutes
MAX_POSTS_PER_CYCLE = int(os.getenv("MAX_POSTS_PER_CYCLE", "2"))
