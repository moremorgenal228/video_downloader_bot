import os
import subprocess
import telebot

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "Скинь ссылку на видео, скачаю 🔥")

@bot.message_handler(func=lambda m: True)
def download(msg):
    url = msg.text.strip()

    bot.reply_to(msg, "Скачиваю... подожди 🔥")

    output = "video.mp4"

    # yt-dlp скачивает видео
    cmd = [
        "yt-dlp",
        "-o", output,
        url
    ]
    subprocess.run(cmd)

    with open(output, "rb") as f:
        bot.send_video(msg.chat.id, f)

bot.polling(none_stop=True)