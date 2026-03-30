import telebot
import yt_dlp
import os
import uuid

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

def download_video(url):
    filename = f"video_{uuid.uuid4()}.mp4"

    ydl_opts = {
        'outtmpl': filename,
        'format': 'best[ext=mp4]',
        'noplaylist': True,
        'quiet': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return filename

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text.strip()

    if not url.startswith("http"):
        bot.reply_to(message, "Gửi link hợp lệ đi bro 😅")
        return

    msg = bot.reply_to(message, "⏳ Đang tải video...")

    try:
        file_path = download_video(url)

        file_size = os.path.getsize(file_path)

        # Telegram limit ~50MB
        if file_size > 50 * 1024 * 1024:
            bot.edit_message_text("⚠️ Video quá nặng (>50MB), không gửi được.", message.chat.id, msg.message_id)
            os.remove(file_path)
            return

        with open(file_path, 'rb') as f:
            bot.send_video(message.chat.id, f)

        os.remove(file_path)

    except Exception as e:
        bot.edit_message_text(f"❌ Lỗi: {str(e)}", message.chat.id, msg.message_id)

bot.infinity_polling()
