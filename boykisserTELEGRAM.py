BOT_TOKEN = "ADD YOUR TELEGRAM BOT TOKEN HERE"



import os
import re
import asyncio
import time
from pathlib import Path
from yt_dlp import YoutubeDL
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
import random

DOWNLOAD_DIR = Path.home() / "Downloads" / "TelegramBotDownloads"
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

YDL_OPTIONS = {
    'outtmpl': str(DOWNLOAD_DIR / '%(title).200s.%(ext)s'),
    'quiet': True,
    'no_warnings': True,
    'noplaylist': True,
    'cookiefile': 'cookies.txt',
}

# === Regex for URLs ===
URL_REGEX = r'(https?://[^\s,]+)'

# === Error Message Pools ===
TOO_BIG_MSGS = [
    "uhuh, cant send it.. MRFFF TOO BIGG~ (>50MB)",
    "it's too thicc for Telegram >///<",
    "hewwp, file too huge for my paws!! qwq",
]

NOT_READY_MSGS = [
    "file still cookin'... didn't finish in time T_T",
    "waited for the file but it ghosted me... >n<",
]

DOWNLOAD_FAIL_MSGS = [
    "eep! download broke... sowwy qwq",
    "i tried but yt-dlp said no :c",
    "it poofed before i could grab it ;_;",
]

NO_VIDEO_MSGS = [
    "i peeked inside the link... no video there o.o",
    "nothing to download? maybe the vid is gone?",
    "video's hiding or deleted... can't find it >~<",
]

# === Wait for File Ready ===
def wait_for_file_ready(path: Path, timeout=30, interval=1) -> bool:
    start_time = time.time()
    last_size = -1
    while time.time() - start_time < timeout:
        if path.exists():
            current_size = path.stat().st_size
            if current_size > 0 and current_size == last_size:
                return True
            last_size = current_size
        time.sleep(interval)
    return False

# === Download and Send Handler ===
async def download_and_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text
    urls = re.findall(URL_REGEX, text)

    if not urls:
        await update.message.reply_text("I need a linkie to snag :3")
        return

    await update.message.reply_text(f"Found {len(urls)} link(s). Processing...")

    for url in urls:
        try:
            await update.message.reply_text(f"Snagging:\n{url}")

            with YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
                if not info:
                    await update.message.reply_text(random.choice(NO_VIDEO_MSGS))
                    continue

                ydl.download([url])
                final_path_str = info.get('requested_downloads', [{}])[0].get('filepath')
                file_path = Path(final_path_str) if final_path_str else Path(ydl.prepare_filename(info))

            # Wait until file is ready
            if not wait_for_file_ready(file_path):
                await update.message.reply_text(random.choice(NOT_READY_MSGS))
                continue

            # Check size
            max_size = 200 * 1024 * 1024
            if file_path.stat().st_size > max_size:
                await update.message.reply_text(f"{random.choice(TOO_BIG_MSGS)}\n`{file_path.name}`")
                continue

            # Send file
            with open(file_path, "rb") as f:
                await update.message.reply_video(
                    video=InputFile(f, filename=file_path.name),
                    supports_streaming=True
                )

        except Exception as e:
            err_msg = str(e).lower()
            if any(term in err_msg for term in ["no video", "unavailable", "extract", "not found"]):
                await update.message.reply_text(f"{random.choice(NO_VIDEO_MSGS)}\n`{url}`")
            else:
                await update.message.reply_text(f"{random.choice(DOWNLOAD_FAIL_MSGS)}\n`{url}`")
            continue

        finally:
            try:
                if 'file_path' in locals() and file_path.exists():
                    file_path.unlink()
            except Exception as e:
                print(f"Cleanup error: {e}")

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), download_and_send))
    print("Bot is running...")
    await app.run_polling()

import sys
import asyncio
if __name__ == "__main__":
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    import telegram.ext

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), download_and_send))

    print("Bot is running...")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(app.run_polling())
    finally:
        loop.run_until_complete(app.shutdown())
        loop.close()
