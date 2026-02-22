import os
import sys
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    sys.exit("Ошибка: BOT_TOKEN не задан. Добавьте BOT_TOKEN в .env")
