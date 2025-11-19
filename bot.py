import os
import subprocess
import telebot
from telebot import types
from yt_dlp import YoutubeDL

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)


# -------------------------------
# Настройки для yt-dlp (рабочие)
# -------------------------------
YDL_OPTS_VIDEO = {
    "format": "best",
    "outtmpl": "%(title)s.%(ext)s",
    "extractor_args": {
        "youtube": {
            "player_client": ["android"]
        }
    }
}

YDL_OPTS_AUDIO = {
    "format": "bestaudio/best",
    "outtmpl": "%(title)s.%(ext)s",
    "extractaudio": True,
    "audioformat": "mp3",
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "mp3",
        "preferredquality": "192",
    }],
    "extractor_args": {
        "youtube": {
            "player_client": ["android"]
        }
    }
}



# ---------------------------------
# /start
# ---------------------------------
@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "Скинь ссылку на видео — и выбери формат 🔥")



# ---------------------------------
# Пользователь присылает ссылку
# ---------------------------------
@bot.message_handler(func=lambda m: m.text.startswith("http"))
def choose_format(msg):
    url = msg.text.strip()

    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("🎬 MP4 (видео)", callback_data=f"mp4|{url}"),
        types.InlineKeyboardButton("🎧 MP3 (аудио)", callback_data=f"mp3|{url}")
    )

    bot.reply_to(msg, "Выбери формат скачивания:", reply_markup=kb)



# ---------------------------------
# Загрузка видео
# ---------------------------------
def download_video(url):
    try:
        with YoutubeDL(YDL_OPTS_VIDEO) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return filename
    except Exception as e:
        return None



# ---------------------------------
# Загрузка аудио
# ---------------------------------
def download_audio(url):
    try:
        with YoutubeDL(YDL_OPTS_AUDIO) as ydl:
            info = ydl.extract_info(url, download=True)
            base = ydl.prepare_filename(info)
            mp3 = base.rsplit(".", 1)[0] + ".mp3"
            return mp3
    except Exception as e:
        return None



# ---------------------------------
# Обработка кнопок
# ---------------------------------
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    format_type, url = call.data.split("|")

    bot.edit_message_text(
        "Скачиваю… подожди 🔥",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id
    )

    if format_type == "mp4":
        filepath = download_video(url)
        if filepath and os.path.exists(filepath):
            with open(filepath, "rb") as f:
                bot.send_video(call.message.chat.id, f)
        else:
            bot.send_message(call.message.chat.id, "⚠️ Не удалось скачать видео.")

    elif format_type == "mp3":
        filepath = download_audio(url)
        if filepath and os.path.exists(filepath):
            with open(filepath, "rb") as f:
                bot.send_audio(call.message.chat.id, f)
        else:
            bot.send_message(call.message.chat.id, "⚠️ Не удалось скачать аудио.")




# ---------------------------------
# Запуск бота
# ---------------------------------
bot.polling(none_stop=True)