import os
import logging
import re
import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    logging.error("❌ BOT_TOKEN không tồn tại! Kiểm tra Variables trên Railway.")
    sys.exit(1)   # Dừng nếu thiếu token

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Bot đã hoạt động!\n\n"
        "Gửi bất kỳ link video nào từ:\n"
        "• YouTube\n• Facebook\n• TikTok\n• Instagram\n• ... \n"
        "Mình sẽ cố gắng tải về cho bạn."
    )

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    urls = re.findall(r'https?://\S+', text)
    if not urls:
        await update.message.reply_text("❌ Không tìm thấy link video nào!")
        return

    url = urls[0]
    msg = await update.message.reply_text("⏳ Đang tải video... (có thể mất 10-40 giây)")

    try:
        import yt_dlp

        ydl_opts = {
            'outtmpl': 'video_%(id)s.%(ext)s',
            'format': 'best[height<=720]/best',   # Giới hạn chất lượng để tránh file quá lớn
            'noplaylist': True,
            'quiet': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        if os.path.exists(filename):
            size_mb = os.path.getsize(filename) / (1024 * 1024)
            caption = f"✅ {info.get('title', 'Video')[:100]}\n📏 {size_mb:.1f} MB"

            if size_mb < 45:
                await msg.edit_text("✅ Tải xong! Đang gửi video...")
                await update.message.reply_video(
                    video=open(filename, 'rb'),
                    caption=caption,
                    supports_streaming=True
                )
            else:
                await msg.edit_text("✅ Tải xong! File lớn nên gửi Document...")
                await update.message.reply_document(
                    document=open(filename, 'rb'),
                    caption=caption
                )

            os.remove(filename)
        else:
            await msg.edit_text("❌ Không tìm thấy file sau khi tải.")

    except Exception as e:
        error_str = str(e)[:300]
        await msg.edit_text(f"❌ Lỗi khi tải:\n{error_str}\n\nThử gửi link khác nhé!")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    logging.info("🚀 Bot đang chạy bằng polling...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
