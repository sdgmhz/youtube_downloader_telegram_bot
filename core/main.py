import telebot
import os
import logging
import yt_dlp
from dotenv import load_dotenv

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

if not os.path.exists("downloads"):
    os.makedirs("downloads")

load_dotenv()
API_TOKEN = os.environ.get("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)

DOWNLOAD_DIR = "downloads/"


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id, "Give me a valid YouTube url and I will download and upload it here for you")


def download_youtube_video(url):
    downloaded_file = []

    def hook(d):
        if d['status'] == 'finished':
            downloaded_file.append(d['filename'])

    ydl_opts = {
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        'format': 'best',
        'progress_hooks': [hook],  # Hook for getting the filename after download
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    if downloaded_file:
        return downloaded_file[0].replace("\\", "/")  # Returning the downloaded file's path
    return None

@bot.message_handler(func=lambda message: True)
def download_file_url(message):
    logger.info(message.text)
    url = message.text
    try:
        file_path = download_youtube_video(url)
        bot.send_chat_action(message.chat.id, action="upload_video")
        with open(file_path, "rb") as video:
            bot.send_video(chat_id=message.chat.id, reply_to_message_id=message.id, video=open(
                file_path, "rb"), caption="file downloaded successfully, ENJOY!", timeout=120)
        os.remove(file_path)
    except:
        bot.reply_to(message, text="problem downloading the requested file")
        raise


bot.infinity_polling()