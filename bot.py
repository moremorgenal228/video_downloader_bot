import os
import subprocess
import telebot
from telebot import types

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

# Стартовое сообщение
@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "Скинь ссылку на видео — и выбери формат 🔥")

# Когда пользователь присылает ссылку
@bot.message_handler(func=lambda m: m.text.startswith("http"))
def choose_format(msg):
    url = msg.text.strip()

    # Кнопки выбора формата
    kb = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("🎬 MP4 (видео)", callback_data=f"mp4|{url}")
    btn2 = types.InlineKeyboardButton("🎧 MP3 (аудио)", callback_data=f"mp3|{url}")
    kb.add(btn1)
    kb.add(btn2)

    bot.reply_to(msg, "Выбери формат скачивания:", reply_markup=kb)

# Обработка нажатий кнопок
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    format_type, url = call.data.split("|")

    bot.edit_message_text(
        "Скачиваю… подожди 🔥",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id
    )

    if format_type == "mp4":
        output = "video.mp4"
        cmd = ["yt-dlp", "-f", "best", "-o", output, url]

        subprocess.run(cmd)
        with open(output, "rb") as f:
            bot.send_video(call.message.chat.id, f)

    elif format_type == "mp3":
        output = "audio.mp3"
        cmd = [
            "yt-dlp",
            "-x",
            "--audio-format", "mp3",
            "-o", output,
            url
        ]

        subprocess.run(cmd)
        with open(output, "rb") as f:
            bot.send_audio(call.message.chat.id, f)

bot.polling(none_stop=True)