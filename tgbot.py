import logging
import time

from telegram import Bot
import os
import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater
import database
import traslation
import utils

# Replace 'YOUR_BOT_TOKEN' with the token you received from BotFather
BOT_TOKEN = None
CHAT_ID = None
bot_token = os.getenv('TG_BOT_TOKEN')
chat_id = os.getenv('TG_CHAT_ID')
if bot_token:
    BOT_TOKEN = bot_token
else:
    print(f"you must provide a bot token!")
if chat_id:
    CHAT_ID = chat_id
else:
    print(f"you must provide a chat_id!")


async def send_message2bot(message: str):
    bot = Bot(BOT_TOKEN)
    async with bot:
        # print(await bot.get_me())
        print(message)
        await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="MarkdownV2")


async def push_telegram_channel(run_date: str):
    date_all = database.session.query(database.FilmDetailItem).filter_by(
        film_publish_date=run_date.replace("-", "/")).all()
    bot = Bot(BOT_TOKEN)
    for item in date_all:
        poster_url = item.film_poster_url
        # file_name = utils.get_filename_from_url(poster_url)
        # download_file = await utils.download_file(poster_url, "imgs" + os.sep + file_name)

        # get poster url
        tgph_poster = database.session.query(database.TelegramInfo).filter_by(film_detail_id=item.id).first()
        # set message to tg channel
        # Initialize the updater
        async with bot:

            # Local path to the photo to be sent
            photo_path = poster_url

            film_title = item.film_title
            if '|' in film_title:
                film_title = film_title.replace('|', '\|')

            if '#' in film_title:
                film_title = film_title.replace('#', '\#')

            if '-' in film_title:
                film_title = film_title.replace('-', '\-')

            if '.' in film_title:
                film_title = film_title.replace('.', ' ')
            if '`' in film_title:
                film_title = film_title.replace('`', ' ')

            # do translate title
            translated_texts = {}
            try:
                translated_texts = await traslation.translate_text(film_title, 'JP', ['ZH', ])
            except Exception as e:
                print(f">>> 翻译作品标题失败: {e}")
                translated_texts['ZH'] = ''
            # Caption for the photo
            formatted_date = run_date.replace("-", "")
            caption = (f"番号: `{item.film_code}`, 演员: `{item.film_stars}`\n"
                       f"标题: `{film_title}`\n"
                       f"```{translated_texts['ZH']}```\n"
                       f"\#D{formatted_date}")

            # URLs for the buttons
            url1 = f'https://netflav5.com/search?type=title&keyword={item.film_code}#query#jump#{item.film_code}'
            url2 = f'{tgph_poster.telegraph_post_url}'

            # Create an InlineKeyboardMarkup with two buttons
            keyboard = [
                [InlineKeyboardButton("去NETFLAV观看", url=url1),
                 InlineKeyboardButton("去Telegraph查看明细", url=url2)],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Send the photo with the caption and buttons
            await bot.send_photo(chat_id=CHAT_ID, photo=photo_path, caption=caption, reply_markup=reply_markup,
                                 parse_mode='MarkdownV2')
            await asyncio.sleep(1)
            tgph_poster.has_push_channel = True
            try:
                database.session.commit()
            except Exception as e:
                print(f"更新记录失败: {e}")
                database.session.rollback()
            print(f">>> Telegram 频道推送任务已完成")


if __name__ == '__main__':
    # asyncio.run(send_message2bot("你好"))
    asyncio.run(push_telegram_channel("2002-06-14"))
