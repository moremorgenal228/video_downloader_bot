import os
import time
import telebot
from telebot import types
from yt_dlp import YoutubeDL

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

YDL_OPTS_VIDEO = {
    "format": "best",
    "outtmpl": "%(title)s.%(ext)s",
    "extractor_args": {
        "youtube": {
            "player_client": ["android", "android_music", "web_safari"]
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
            "player_client": ["android", "android_music", "web_safari"]
        }
    }
}

@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "Кидай ссылку на видео 🔥")

@bot.message_handler(func=lambda m: m.text.startswith("http"))
def choose_format(msg):
    url = msg.text.strip()
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("🎬 Видео (MP4)", callback_data=f"mp4|{url}"),
        types.InlineKeyboardButton("🎧 Аудио (MP3)", callback_data=f"mp3|{url}")
    )
    bot.reply_to(msg, "Выбери формат:", reply_markup=kb)

def download_video(url):
    try:
        with YoutubeDL(YDL_OPTS_VIDEO) as ydl:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info)
    except:
        return None

def download_audio(url):
    try:
        with YoutubeDL(YDL_OPTS_AUDIO) as ydl:
            info = ydl.extract_info(url, download=True)
            base = ydl.prepare_filename(info)
            mp3 = base.rsplit(".", 1)[0] + ".mp3"

            # Ждём, пока файл реально появится
            for _ in range(10):
                if os.path.exists(mp3):
                    break
                time.sleep(1)

            return mp3
    except:
        return None

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    ftype, url = call.data.split("|")

    bot.edit_message_text("Скачиваю… 🔥", call.message.chat.id, call.message.message_id)

    if ftype == "mp4":
        path = download_video(url)
        if path and os.path.exists(path):
            with open(path, "rb") as f:
                bot.send_video(call.message.chat.id, f)
        else:
            bot.send_message(call.message.chat.id, "⚠️ Не удалось скачать видео.")

    elif ftype == "mp3":
        path = download_audio(url)
        if path and os.path.exists(path):
            with open(path, "rb") as f:
                bot.send_audio(call.message.chat.id, f)
        else:
            bot.send_message(call.message.chat.id, "⚠️ Не удалось скачать аудио.")

bot.polling(none_stop=True)