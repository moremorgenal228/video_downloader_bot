import os
import telebot
import yt_dlp

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# Настройки для скачивания
ydl_opts_video = {
    "format": "mp4",
    "outtmpl": "video.mp4",
}

ydl_opts_audio = {
    "format": "mp3/bestaudio/best",
    "outtmpl": "audio.mp3",
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }
    ],
}

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Отправь ссылку на видео, и я скачаю его для тебя 😉")

@bot.message_handler(content_types=['text'])
def download(message):
    url = message.text.strip()

    if not url.startswith("http"):
        bot.reply_to(message, "Отправь корректную ссылку 🙂")
        return

    bot.send_message(message.chat.id, "⏳ Скачиваю, подожди пару секунд...")

    try:
        # Скачивание видео
        with yt_dlp.YoutubeDL(ydl_opts_video) as ydl:
            ydl.download([url])

        # Отправка видео
        with open("video.mp4", "rb") as f:
            bot.send_video(message.chat.id, f)

        os.remove("video.mp4")

    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")

bot.polling(none_stop=True)