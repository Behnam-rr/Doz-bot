import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_member(update, context):
        keyboard = [[InlineKeyboardButton("عضویت در کانال 📢", url="https://t.me/Ya4DeT")]]
        await update.message.reply_text("⚠️ برای استفاده از ربات باید در کانال ما عضو بشی!", reply_markup=InlineKeyboardMarkup(keyboard))
        return
    await update.message.reply_text("سلام! 👋\n\nلینک بفرست تا دانلود کنم:\n🎬 ویدیو: TikTok, Instagram\n🎵 موزیک: /music لینک_ساندکلود")

async def get_url(update):
    if update.message.text:
        return update.message.text.strip()
    if update.message.entities:
        for entity in update.message.entities:
            if entity.type == "url":
                return update.message.text[entity.offset:entity.offset + entity.length]
    return None

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_member(update, context):
        keyboard = [[InlineKeyboardButton("عضویت در کانال 📢", url="https://t.me/Ya4DeT")]]
        await update.message.reply_text("⚠️ برای استفاده از ربات باید در کانال ما عضو بشی!", reply_markup=InlineKeyboardMarkup(keyboard))
        return
    url = await get_url(update)
    if not url or not url.startswith("http"):
        return
    msg = await update.message.reply_text("⏳ دارم ویدیو رو دانلود میکنم...")
    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': '/tmp/%(title)s.%(ext)s',
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        width = info.get('width')
        height = info.get('height')
        with open(filename, 'rb') as f:
            await update.message.reply_video(f, width=width, height=height, supports_streaming=True)
        os.remove(filename)
        await msg.delete()
    except Exception as e:
        await msg.edit_text("❌ خطا! لینک رو چک کن.")

async def music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_member(update, context):
        keyboard = [[InlineKeyboardButton("عضویت در کانال 📢", url="https://t.me/Ya4DeT")]]
        await update.message.reply_text("⚠️ برای استفاده از ربات باید در کانال ما عضو بشی!", reply_markup=InlineKeyboardMarkup(keyboard))
        return
    url = None
    if context.args:
        url = context.args[0]
    elif update.message.entities:
        for entity in update.message.entities:
            if entity.type == "url":
                url = update.message.text[entity.offset:entity.offset + entity.length]
    if not url:
        await update.message.reply_text("لینک رو بعد از /music بنویس!\nمثال: /music https://soundcloud.com/...")
        return
    msg = await update.message.reply_text("⏳ دارم موزیک رو دانلود میکنم...")
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': '/tmp/%(title)s.%(ext)s',
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}],
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')
        with open(filename, 'rb') as f:
            await update.message.reply_audio(f, title=info.get('title', 'موزیک'))
        os.remove(filename)
        await msg.delete()
    except Exception as e:
        await msg.edit_text("❌ خطا! لینک رو چک کن.")

TOKEN = os.environ["TOKEN"]
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("music", music))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
app.run_polling()
