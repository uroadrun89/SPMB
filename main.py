import logging
import os
import time
import subprocess
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Logging configuration
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Define your Telegram bot token directly in the code
TELEGRAM_TOKEN = '6869431049:AAFiUSeKNLctZrSjb-tk8G0DtMrmDkj33rM'

if not TELEGRAM_TOKEN:
    logger.error("Telegram token is not defined. Set the TELEGRAM_TOKEN variable in the code.")
    raise ValueError("Telegram token is not defined.")

# Ensure spotdl can download FFmpeg and handle issues if any
try:
    subprocess.run(['spotdl', '--download-ffmpeg'], check=True)
except Exception as e:
    logger.error(f"Error executing spotdl command: {e}")

class Config:
    def __init__(self):
        self.token = TELEGRAM_TOKEN
        self.auth_enabled = False  # Change to True if authentication is required
        self.auth_password = "your_password"  # Set the desired authentication password
        self.auth_users = []  # List of authorized user chat IDs

config = Config()

def authenticate(func):
    def wrapper(update: Update, context: CallbackContext):
        chat_id = update.effective_chat.id
        if config.auth_enabled:
            if chat_id not in config.auth_users:
                context.bot.send_message(chat_id=chat_id, text="⚠️ The password was incorrect")
                return
        return func(update, context)
    return wrapper

def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text="🎵 Welcome to the Song Downloader Bot! 🎵")

def get_single_song(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message_id = update.effective_message.message_id
    logger.info(f'Starting song download. Chat ID: {chat_id}, Message ID: {message_id}')

    url = update.effective_message.text.strip()

    logger.info('Downloading song...')
    context.bot.send_message(chat_id=chat_id, text="🔍 Downloading")

    if url.startswith(("http://", "https://")):
        try:
            # Use /tmp for temporary files
            download_dir = "/tmp/song_download"
            os.makedirs(download_dir, exist_ok=True)
            os.chdir(download_dir)

            # Download the song using spotdl
            subprocess.run(['spotdl', 'download', url, '--threads', '12', '--format', 'm4a', '--lyrics', 'genius'], check=True)

            # Send the song file to the user
            files = [file for file in os.listdir(".") if file.endswith(".m4a")]
            if files:
                for file in files:
                    try:
                        with open(file, 'rb') as audio_file:
                            context.bot.send_audio(chat_id=chat_id, audio=audio_file, timeout=18000)
                        logger.info('Sent audio file to user.')
                        time.sleep(0.3)  # Add a delay of 0.3 seconds between sending each audio file
                    except Exception as e:
                        logger.error(f"Error sending audio: {e}")
                logger.info(f'Sent {len(files)} audio file(s) to user.')
            else:
                context.bot.send_message(chat_id=chat_id, text="❌ Unable to find the requested song.")
                logger.warning('No audio file found after download.')
        except subprocess.CalledProcessError as e:
            logger.error(f"Error during download: {e}")
            context.bot.send_message(chat_id=chat_id, text="❌ Failed to download the song. Please try again.")
        except Exception as e:
            logger.error(f"Error during processing: {e}")
            context.bot.send_message(chat_id=chat_id, text="❌ Failed to process the song. Please try again.")
        finally:
            # Clean up temporary directory
            os.chdir('/tmp')
            subprocess.run(['rm', '-rf', download_dir], check=True)
    else:
        context.bot.send_message(chat_id=chat_id, text="❌ Invalid URL. Please provide a valid song URL.")
        logger.warning('Invalid URL provided.')

def main():
    updater = Updater(token=config.token, use_context=True)
    dispatcher = updater.dispatcher

    # Handlers
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    song_handler = MessageHandler(Filters.text & (~Filters.command), get_single_song)
    dispatcher.add_handler(song_handler)

    # Start the bot
    updater.start_polling(poll_interval=0.3)
    logger.info('Bot started')
    updater.idle()

if __name__ == "__main__":
    main()
