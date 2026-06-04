import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    await update.message.reply_text("⏳ دارم دانلود میکنم...")
    try:
        ydl_opts = {
            'format': 'best[filesize<50M]/best',
            'outtmpl': '/tmp/%(title)s.%(ext)s',
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        with open(filename, 'rb') as f:
            await update.message.reply_video(f)
        os.remove(filename)
    except Exception as e:
        await update.message.reply_text("❌ خطا! لینک رو چک کن.")

TOKEN = os.environ["TOKEN"]
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT, download))
app.run_polling()

