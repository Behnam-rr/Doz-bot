import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

CHANNEL = "@Ya4DeT"

async def check_member(update: Update, context):
    user_id = update.message.from_user.id
    try:
        member = await context.bot.get_chat_member(CHANNEL, user_id)
        if member.status in ["member", "administrator", "creator"]:
            return True
    except:
        pass
    return False

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_member(update, context):
        keyboard = [[InlineKeyboardButton("عضویت در کانال 📢", url=f"https://t.me/Ya4DeT")]]
        await update.message.reply_text(
            "⚠️ برای استفاده از ربات باید در کانال ما عضو بشی!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

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
