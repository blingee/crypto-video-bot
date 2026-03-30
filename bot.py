import os
import logging
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("8630924673:AAFze-ZdI5L-__WeF9ao__I9DB10aiBQCDU")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Xin chào! Gửi link video từ YouTube, Facebook, TikTok, Instagram, X... mình sẽ tải về cho bạn.\n"
        "Video lớn sẽ được nén hoặc gửi dưới dạng Document."
    )

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    # Tìm link trong tin nhắn
    urls = re.findall(r'https?://\S+', text)
    if not urls:
        await update.message.reply_text("❌ Không tìm thấy link video nào!")
        return

    url = urls[0]
    msg = await update.message.reply_text("⏳ Đang xử lý và tải video... chờ mình chút nhé!")

    try:
        ydl_opts = {
            'outtmpl': 'video_%(id)s.%(ext)s',
            'format': 'best[height<=720]/best',   # Giới hạn 720p để giảm kích thước
            'noplaylist': True,
            'quiet': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        if os.path.exists(filename):
            file_size_mb = os.path.getsize(filename) / (1024 * 1024)

            caption = f"✅ {info.get('title', 'Video')[:100]}\n📏 {file_size_mb:.1f} MB"

            if file_size_mb < 45:   # An toàn dưới giới hạn video
                await msg.edit_text("✅ Tải xong! Đang gửi video...")
                await update.message.reply_video(
                    video=open(filename, 'rb'),
                    caption=caption,
                    supports_streaming=True
                )
            else:
                await msg.edit_text("✅ Tải xong! File hơi lớn, gửi dưới dạng Document...")
                await update.message.reply_document(
                    document=open(filename, 'rb'),
                    caption=caption
                )

            os.remove(filename)  # Xóa file sau khi gửi
        else:
            await msg.edit_text("❌ Không tìm thấy file sau khi tải.")

    except Exception as e:
        error = str(e)[:250]
        await msg.edit_text(f"❌ Lỗi khi tải: {error}\nThử gửi link khác nhé!")

def main():
    if not TOKEN:
        print("❌ Chưa set BOT_TOKEN!")
        return

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    print("🚀 Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
