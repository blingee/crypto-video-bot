import os
import logging
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", 8080))   # Railway tự cung cấp PORT

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Bot đã sẵn sàng!\n"
        "Gửi link video YouTube, Facebook, TikTok, Instagram... mình sẽ tải về cho bạn."
    )

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    urls = re.findall(r'https?://\S+', text)
    if not urls:
        await update.message.reply_text("❌ Không tìm thấy link video!")
        return

    url = urls[0]
    msg = await update.message.reply_text("⏳ Đang tải video... chờ chút nhé!")

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
                await msg.edit_text("✅ Tải xong! Đang gửi video...")
                await update.message.reply_video(video=open(filename, 'rb'), caption=caption, supports_streaming=True)
            else:
                await msg.edit_text("✅ Tải xong! File lớn, gửi Document...")
                await update.message.reply_document(document=open(filename, 'rb'), caption=caption)

            os.remove(filename)
        else:
            await msg.edit_text("❌ Không tìm thấy file video.")

    except Exception as e:
        await msg.edit_text(f"❌ Lỗi: {str(e)[:200]}")

def main():
    if not TOKEN:
        logging.error("BOT_TOKEN chưa được thiết lập!")
        return

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    # Webhook mode cho Railway
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,                    # Dùng token làm path để bảo mật
        webhook_url=f"https://{os.getenv('RAILWAY_PUBLIC_DOMAIN', 'your-domain')}/{TOKEN}"
    )

if __name__ == "__main__":
    main()
