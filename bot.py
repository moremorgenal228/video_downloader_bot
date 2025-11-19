import os
from aiogram import Bot, Dispatcher, executor, types
import yt_dlp
import asyncio

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

DOWNLOAD_DIR = "/tmp"


# === функции скачивания ===
def download_video(url, quality):
    """
    quality:
      - best     (максимум)
      - 1080p
      - 480p
      - 360p
    """

    format_map = {
        "best": "best",
        "1080p": "bestvideo[height=1080]+bestaudio/best",
        "480p": "bestvideo[height=480]+bestaudio/best",
        "360p": "bestvideo[height=360]+bestaudio/best",
    }

    ydl_opts = {
        "outtmpl": f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
        "merge_output_format": "mp4",
        "format": format_map.get(quality, "best"),
        "noplaylist": True,
        "quiet": True,
        "extractor_args": {
            "youtube": {
                "player_client": ["default"]
            }
        },
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)


def download_audio(url):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": f"{DOWNLOAD_DIR}/%(title)s.mp3",
        "quiet": True,
        "noplaylist": True,
        "extractor_args": {
            "youtube": {
                "player_client": ["default"]
            }
        },
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)


# === команды ===
@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    await message.answer(
        "Скидывай ссылку на YouTube 🎥\n"
        "Я подготовлю варианты скачивания 🔥"
    )


# === обработка ссылок ===
@dp.message_handler()
async def get_url(message: types.Message):
    url = message.text.strip()

    if "youtu" not in url:
        await message.answer("Это не похоже на YouTube ссылку 🙂")
        return

    # Кнопки выбора качества
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("🎥 MP4 1080p", callback_data=f"v1080|{url}"),
        types.InlineKeyboardButton("🎥 MP4 480p",  callback_data=f"v480|{url}"),
    )
    kb.add(
        types.InlineKeyboardButton("🎥 MP4 360p",  callback_data=f"v360|{url}"),
    )
    kb.add(
        types.InlineKeyboardButton("🎧 MP3",       callback_data=f"mp3|{url}")
    )

    await message.answer("Выбери формат 👇", reply_markup=kb)


# === обработка кнопок ===
@dp.callback_query_handler()
async def process_callback(call: types.CallbackQuery):
    action, url = call.data.split("|")

    await call.message.edit_text("Скачиваю… подожди пару секунд ⏳")

    try:
        if action == "mp3":
            path = download_audio(url)
            await call.message.answer_audio(open(path, "rb"))
            os.remove(path)

        elif action == "v1080":
            path = download_video(url, "1080p")
            await call.message.answer_video(open(path, "rb"))
            os.remove(path)

        elif action == "v480":
            path = download_video(url, "480p")
            await call.message.answer_video(open(path, "rb"))
            os.remove(path)

        elif action == "v360":
            path = download_video(url, "360p")
            await call.message.answer_video(open(path, "rb"))
            os.remove(path)

        else:
            await call.message.answer("Неизвестный формат 🤔")

    except Exception as e:
        await call.message.answer(f"Ошибка: {e}")


if name == "__main__":
    executor.start_polling(dp, skip_updates=True)