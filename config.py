import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

REACTIONS = {
    "💋": "Kiss",
    "💍": "Marry",
    "🔪": "Kill"
}

WAIFU_API = "https://api.waifu.pics/sfw/waifu"