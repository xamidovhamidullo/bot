from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import yt_dlp as youtube_dl
from TikTokApi import TikTokApi
import os
import asyncio
import aiohttp

TOKEN = '7463160856:AAEGj67ck4zdYbjstbZUf6o6_V1NSBDU2m8'


async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Send a link to download the video.')


async def download_video(update: Update, context: CallbackContext) -> None:
    url = update.message.text
    if 'youtube.com' in url or 'youtu.be' in url:
        await download_youtube_video(url, update, context)
    elif 'tiktok.com' in url:
        await download_tiktok_video(url, update, context)
    elif 'instagram.com' in url:
        await download_instagram_video(url, update)
    else:
        await update.message.reply_text('Unsupported URL. Please send a YouTube, TikTok, or Instagram link.')


async def download_youtube_video(url: str, update: Update, context: CallbackContext) -> None:
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.mp4',
    }
    loop = asyncio.get_event_loop()
    info_dict = await loop.run_in_executor(None,
                                           lambda: youtube_dl.YoutubeDL(ydl_opts).extract_info(url, download=True))
    filename = youtube_dl.YoutubeDL(ydl_opts).prepare_filename(info_dict)
    await update.message.reply_text(f'Downloading YouTube video: {filename}')

    # Sending video file
    with open(filename, 'rb') as video_file:
        await context.bot.send_video(chat_id=update.message.chat_id, video=video_file)
    os.remove(filename)


async def download_tiktok_video(url: str, update: Update, context: CallbackContext) -> None:
    try:
        api = TikTokApi()
        video_id = url.split('/')[-1]
        video_data = api.video_download(video_id)
        filename = 'tiktok_video.mp4'

        with open(filename, 'wb') as f:
            f.write(video_data)

        await update.message.reply_text(f'Downloading TikTok video: {filename}')

        with open(filename, 'rb') as video_file:
            await context.bot.send_video(chat_id=update.message.chat_id, video=video_file)
        os.remove(filename)
    except Exception as e:
        await update.message.reply_text(f'Error downloading TikTok video: {str(e)}')


async def download_instagram_video(url: str, update: Update) -> None:
    await update.message.reply_text('Instagram video download is not yet implemented.')


async def main() -> None:
    application =  Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    await application.run_polling()


if __name__ == '__main__':
    asyncio.run(main())
