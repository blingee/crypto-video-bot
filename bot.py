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

# Lấy token từ biến môi trường
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    logging.error("❌ BOT_TOKEN không tìm thấy! Kiểm tra Variables trên Railway.")
    # Không exit ở đây để build vẫn thành công
    TOKEN = "DUMMY"  # placeholder cho build phase

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Bot tải video đã sẵn sàng!\n\n"
        "Gửi link video từ YouTube, Facebook, TikTok, Instagram... mình sẽ tải về."
    )

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    urls = re.findall(r'https?://\S+', text)
    if not urls:
        await update.message.reply_text("❌ Không tìm thấy link video!")
        return

    url = urls[0]
    msg = await update.message.reply_text("⏳ Đang tải video... chờ mình chút (10-40 giây)")

    try:
        import yt_dlp
        ydl_opts = {
            'outtmpl': 'video_%(id)s.%(ext)s',
            'format': 'best[height<=720]/best',
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
                await msg.edit_text("✅ Tải xong → gửi video...")
                await update.message.reply_video(video=open(filename, 'rb'), caption=caption, supports_streaming=True)
            else:
                await msg.edit_text("✅ Tải xong → gửi Document...")
                await update.message.reply_document(document=open(filename, 'rb'), caption=caption)

            os.remove(filename)
        else:
            await msg.edit_text("❌ Không tìm thấy file video.")

    except Exception as e:
        await msg.edit_text(f"❌ Lỗi: {str(e)[:250]}\nThử link khác nhé!")

def main():
    if TOKEN == "DUMMY" or not TOKEN:
        logging.error("❌ BOT_TOKEN chưa được thiết lập trên Railway!")
        return

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    logging.info("🚀 Bot đang chạy bằng polling...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
