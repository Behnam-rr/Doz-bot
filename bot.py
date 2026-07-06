import os
import io
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, CallbackQueryHandler, filters, ContextTypes

CHANNEL = "@Ya4DeT"
ADMIN_ID = 6517505210
users = set()
waiting_for_video = set()
waiting_for_support = set()
user_lang = {}

TEXTS = {
    'fa': {
        'join': '⚠️ برای استفاده از ربات باید در کانال ما عضو بشی!',
        'join_btn': 'عضویت در کانال 📢',
        'start': 'سلام! 👋\n\nلینک بفرست تا دانلود کنم:\n🎬 ویدیو: TikTok, Instagram\n🎵 موزیک: /music لینک\n🎤 تبدیل ویدیو: /tomp3\n💬 پشتیبانی: /support\n🌐 زبان: /lang',
        'downloading': '⏳ دارم دانلود میکنم...',
        'error': '❌ خطا! لینک رو چک کن.',
        'converting': '⏳ دارم تبدیل میکنم...',
        'send_video': '🎬 ویدیو رو بفرست!',
        'convert_error': '❌ خطا! ویدیو رو دوباره بفرست.',
        'support_msg': '💬 پیامت رو بنویس، به ادمین میرسونم!',
        'support_sent': '✅ پیامت به ادمین رسید!',
        'music_help': 'لینک رو بعد از /music بنویس!',
        'music_downloading': '⏳ دارم موزیک رو دانلود میکنم...',
        'choose_lang': '🌐 زبان رو انتخاب کن:',
        'lang_set': '✅ زبان تغییر کرد!',
    },
    'en': {
        'join': '⚠️ You must join our channel to use this bot!',
        'join_btn': 'Join Channel 📢',
        'start': 'Hello! 👋\n\nSend a link to download:\n🎬 Video: TikTok, Instagram\n🎵 Music: /music link\n🎤 Convert video: /tomp3\n💬 Support: /support\n🌐 Language: /lang',
        'downloading': '⏳ Downloading...',
        'error': '❌ Error! Check the link.',
        'converting': '⏳ Converting...',
        'send_video': '🎬 Send me a video!',
        'convert_error': '❌ Error! Send the video again.',
        'support_msg': '💬 Write your message, I will send it to admin!',
        'support_sent': '✅ Your message was sent to admin!',
        'music_help': 'Send link after /music!',
        'music_downloading': '⏳ Downloading music...',
        'choose_lang': '🌐 Choose your language:',
        'lang_set': '✅ Language changed!',
    },
    'ku': {
        'join': '⚠️ دەبێت بەندە بیت بە کەناڵەکەمان بۆ بەکارهێنانی بۆتەکە!',
        'join_btn': 'بەندەبوون بە کەناڵ 📢',
        'start': 'سڵاو! 👋\n\nلینک بنێرە بۆ داونلۆدکردن:\n🎬 ڤیدیۆ: TikTok, Instagram\n🎵 موزیک: /music لینک\n🎤 گۆڕینی ڤیدیۆ: /tomp3\n💬 پاڵپشتی: /support\n🌐 زمان: /lang',
        'downloading': '⏳ داونلۆد دەکەم...',
        'error': '❌ هەڵە! لینکەکە بپشکنە.',
        'converting': '⏳ دەیگۆڕم...',
        'send_video': '🎬 ڤیدیۆ بنێرە!',
        'convert_error': '❌ هەڵە! ڤیدیۆکە دووبارە بنێرە.',
        'support_msg': '💬 پەیامەکەت بنووسە!',
        'support_sent': '✅ پەیامەکەت گەیشتە ئەدمین!',
        'music_help': 'لینک بنووسە دوای /music!',
        'music_downloading': '⏳ موزیک داونلۆد دەکەم...',
        'choose_lang': '🌐 زمانەکەت هەڵبژێرە:',
        'lang_set': '✅ زمان گۆڕدرا!',
    },
    'ar': {
        'join': '⚠️ يجب عليك الانضمام إلى قناتنا لاستخدام البوت!',
        'join_btn': 'انضم إلى القناة 📢',
        'start': 'مرحباً! 👋\n\nأرسل رابطاً للتحميل:\n🎬 فيديو: TikTok, Instagram\n🎵 موسيقى: /music رابط\n🎤 تحويل الفيديو: /tomp3\n💬 الدعم: /support\n🌐 اللغة: /lang',
        'downloading': '⏳ جاري التحميل...',
        'error': '❌ خطأ! تحقق من الرابط.',
        'converting': '⏳ جاري التحويل...',
        'send_video': '🎬 أرسل الفيديو!',
        'convert_error': '❌ خطأ! أرسل الفيديو مرة أخرى.',
        'support_msg': '💬 اكتب رسالتك، سأرسلها إلى المشرف!',
        'support_sent': '✅ تم إرسال رسالتك إلى المشرف!',
        'music_help': 'أرسل الرابط بعد /music!',
        'music_downloading': '⏳ جاري تحميل الموسيقى...',
        'choose_lang': '🌐 اختر لغتك:',
        'lang_set': '✅ تم تغيير اللغة!',
    },
}

def t(user_id, key):
    lang = user_lang.get(user_id, 'fa')
    return TEXTS.get(lang, TEXTS['fa']).get(key, '')

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
    user_id = update.message.from_user.id
    users.add(user_id)
    if not await check_member(update, context):
        keyboard = [[InlineKeyboardButton(t(user_id, 'join_btn'), url="https://t.me/Ya4DeT")]]
        await update.message.reply_text(t(user_id, 'join'), reply_markup=InlineKeyboardMarkup(keyboard))
        return
    await update.message.reply_text(t(user_id, 'start'))

async def lang_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    keyboard = [
        [InlineKeyboardButton("🇮🇷 فارسی", callback_data="lang_fa")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton("🏳️ کوردی سۆرانی", callback_data="lang_ku")],
        [InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar")],
    ]
    await update.message.reply_text(t(user_id, 'choose_lang'), reply_markup=InlineKeyboardMarkup(keyboard))

async def support_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not await check_member(update, context):
        keyboard = [[InlineKeyboardButton(t(user_id, 'join_btn'), url="https://t.me/Ya4DeT")]]
        await update.message.reply_text(t(user_id, 'join'), reply_markup=InlineKeyboardMarkup(keyboard))
        return
    waiting_for_support.add(user_id)
    await update.message.reply_text(t(user_id, 'support_msg'))

async def tomp3_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not await check_member(update, context):
        keyboard = [[InlineKeyboardButton(t(user_id, 'join_btn'), url="https://t.me/Ya4DeT")]]
        await update.message.reply_text(t(user_id, 'join'), reply_markup=InlineKeyboardMarkup(keyboard))
        return
    waiting_for_video.add(user_id)
    await update.message.reply_text(t(user_id, 'send_video'))

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in waiting_for_video:
        return
    waiting_for_video.discard(user_id)
    msg = await update.message.reply_text(t(user_id, 'converting'))
    try:
        video = update.message.video or update.message.document
        file = await context.bot.get_file(video.file_id)
        video_path = f"/tmp/video_{user_id}.mp4"
        await file.download_to_drive(video_path)
        mp3_path = f"/tmp/audio_{user_id}.mp3"
        os.system(f"ffmpeg -i {video_path} -q:a 0 -map a {mp3_path} -y")
        with open(mp3_path, 'rb') as f:
            audio_data = f.read()
        await update.message.reply_audio(io.BytesIO(audio_data), filename="audio.mp3")
        await update.message.reply_voice(io.BytesIO(audio_data))
        os.remove(video_path)
        os.remove(mp3_path)
        await msg.delete()
    except Exception as e:
        await msg.edit_text(t(user_id, 'convert_error'))

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("❌ دسترسی ندارید!")
        return
    keyboard = [
        [InlineKeyboardButton("📊 آمار کاربران", callback_data="stats")],
        [InlineKeyboardButton("📢 پیام همگانی", callback_data="broadcast_prompt")],
    ]
    await update.message.reply_text("👮 پنل ادمین:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data.startswith("lang_"):
        lang = query.data.split("_")[1]
        user_lang[user_id] = lang
        await query.edit_message_text(t(user_id, 'lang_set'))
        return

    if user_id != ADMIN_ID:
        await query.edit_message_text("❌ دسترسی ندارید!")
        return
    if query.data == "stats":
        await query.edit_message_text(f"📊 تعداد کاربران: {len(users)} نفر")
    elif query.data == "broadcast_prompt":
        await query.edit_message_text("برای پیام همگانی بنویس:\n/broadcast متن_پیام")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("متن پیام رو بعد از /broadcast بنویس!")
        return
    text = " ".join(context.args)
    sent = 0
    for user_id in users:
        try:
            await context.bot.send_message(user_id, text)
            sent += 1
        except:
            pass
    await update.message.reply_text(f"✅ پیام به {sent} نفر فرستاده شد!")

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("ID کاربر رو بعد از /ban بنویس!")
        return
    try:
        ban_id = int(context.args[0])
        users.discard(ban_id)
        await update.message.reply_text(f"✅ کاربر {ban_id} بن شد!")
    except:
        await update.message.reply_text("❌ ID اشتباهه!")

async def reply_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("استفاده: /reply ID پیام")
        return
    try:
        target_id = int(context.args[0])
        text = " ".join(context.args[1:])
        await context.bot.send_message(target_id, f"📨 پیام از ادمین:\n{text}")
        await update.message.reply_text("✅ پیام فرستاده شد!")
    except:
        await update.message.reply_text("❌ خطا!")

async def get_url(update):
    if update.message.text:
        return update.message.text.strip()
    if update.message.entities:
        for entity in update.message.entities:
            if entity.type == "url":
                return update.message.text[entity.offset:entity.offset + entity.length]
    return None

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id in waiting_for_support:
        waiting_for_support.discard(user_id)
        username = update.message.from_user.username or "بدون یوزرنیم"
        name = update.message.from_user.first_name or ""
        await context.bot.send_message(
            ADMIN_ID,
            f"📩 پیام پشتیبانی:\n👤 {name} (@{username})\n🆔 ID: {user_id}\n\n{update.message.text}"
        )
        await update.message.reply_text(t(user_id, 'support_sent'))
        return

    users.add(user_id)
    if not await check_member(update, context):
        keyboard = [[InlineKeyboardButton(t(user_id, 'join_btn'), url="https://t.me/Ya4DeT")]]
        await update.message.reply_text(t(user_id, 'join'), reply_markup=InlineKeyboardMarkup(keyboard))
        return
    url = await get_url(update)
    if not url or not url.startswith("http"):
        return
    msg = await update.message.reply_text(t(user_id, 'downloading'))
    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': '/tmp/%(title)s.%(ext)s',
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        ext = filename.split('.')[-1].lower()
        width = info.get('width')
        height = info.get('height')
        with open(filename, 'rb') as f:
            if ext in ['jpg', 'jpeg', 'png', 'webp']:
                await update.message.reply_photo(f)
            else:
                await update.message.reply_video(f, width=width, height=height, supports_streaming=True)
        os.remove(filename)
        await msg.delete()
    except Exception as e:
        await msg.edit_text(t(user_id, 'error'))

async def music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    users.add(user_id)
    if not await check_member(update, context):
        keyboard = [[InlineKeyboardButton(t(user_id, 'join_btn'), url="https://t.me/Ya4DeT")]]
        await update.message.reply_text(t(user_id, 'join'), reply_markup=InlineKeyboardMarkup(keyboard))
        return
    url = None
    if context.args:
        url = context.args[0]
    elif update.message.entities:
        for entity in update.message.entities:
            if entity.type == "url":
                url = update.message.text[entity.offset:entity.offset + entity.length]
    if not url:
        await update.message.reply_text(t(user_id, 'music_help'))
        return
    msg = await update.message.reply_text(t(user_id, 'music_downloading'))
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
        await msg.edit_text(t(user_id, 'error'))

TOKEN = os.environ["TOKEN"]
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("admin", admin))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(CommandHandler("ban", ban))
app.add_handler(CommandHandler("music", music))
app.add_handler(CommandHandler("tomp3", tomp3_cmd))
app.add_handler(CommandHandler("support", support_cmd))
app.add_handler(CommandHandler("reply", reply_to_user))
app.add_handler(CommandHandler("lang", lang_cmd))
app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
app.run_polling()
