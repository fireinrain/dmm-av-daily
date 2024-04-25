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
        first = database.session.query(database.TelegramInfo).filter_by(film_detail_id=item.id).first()
        if first is not None and first.has_push_channel:
            continue
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
            translated_text = ''
            try:
                translated_texts = await traslation.translate_text(film_title, 'JP', ['ZH', ])
                translated_text = translated_texts['ZH'].replace('\r', '').replace('\n', '').replace('\r\n', '')
            except Exception as e:
                print(f">>> 翻译作品标题失败: {e}")

            # Caption for the photo
            formatted_date = run_date.replace("-", "")
            split_star = []
            stars = item.film_stars.replace("-", "")
            if '----' in item.film_stars:
                split_star = ['']
            else:
                split_star = item.film_stars.split(" ")
                if len(split_star) >= 3:
                    split_star = split_star[:3]
                split_star = [f'\#{i}' for i in split_star]
            dvd_id = utils.convert_cid2code(item.film_code)
            # tg markdownv2 不支持字符串中有- 所以要转义,tg caption 不支持-，
            # 所以设置为去掉
            dvd_id2 = dvd_id.replace("-", "")
            caption = (f'番号: `{dvd_id}`, 演员: `{stars}`\n'
                       f'标题: `{film_title}`\n'
                       f'{translated_text}\n'
                       f"\#D{formatted_date} \#{dvd_id2} {' '.join(split_star)}")

            suffix = '#query#jump'
            # URLs for the buttons
            url1 = f'https://Missav.com/search/{item.film_code}'
            url2 = f'https://www5.Javmost.com/search/{item.film_code}'
            url3 = f'https://Jable.tv/search/{item.film_code}'
            url4 = f'https://netflav5.com/search?type=title&keyword={item.film_code}'

            url5 = f'{tgph_poster.telegraph_post_url}'
            # https://Missav.com/search/%s#query#jump
            # https://www5.Javmost.com/search/%s/#query#jump

            # Create an InlineKeyboardMarkup with two buttons
            keyboard = [
                [InlineKeyboardButton("MissAV观看", url=url1),
                 InlineKeyboardButton("JavMost观看", url=url2),
                 InlineKeyboardButton("JableTV观看", url=url3)
                 ],

                [InlineKeyboardButton("Netflav观看", url=url4),
                 InlineKeyboardButton("Telegraph查看明细", url=url5)],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            try:
                # Send the photo with the caption and buttons
                await bot.send_photo(chat_id=CHAT_ID, photo=photo_path, caption=caption, reply_markup=reply_markup,
                                     parse_mode='MarkdownV2', read_timeout=60 * 60, write_timeout=60 * 60,
                                     connect_timeout=60 * 60)
            except Exception as e:
                print(f"推送到频道失败: {e}")
                continue
            await asyncio.sleep(3)
            tgph_poster.has_push_channel = True
            try:
                database.session.commit()
            except Exception as e:
                print(f"更新记录失败: {e}")
                database.session.rollback()
            print(f">>> Telegram 频道推送任务已完成")


async def patch_tg_channel_push():
    bot = Bot(BOT_TOKEN)
    not_pushs = database.session.query(database.TelegramInfo).filter_by(has_push_channel=False).all()
    for item in not_pushs:
        # get poster url
        film_detail = database.session.query(database.FilmDetailItem).filter_by(id=item.film_detail_id).first()
        # set message to tg channel
        # Initialize the updater
        poster_url = film_detail.film_poster_url
        async with bot:

            # Local path to the photo to be sent
            photo_path = poster_url

            film_title = film_detail.film_title
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
            run_date = film_detail.film_publish_date.replace("/", "-")
            # do translate title
            translated_text = ''
            try:
                translated_texts = await traslation.translate_text(film_title, 'JP', ['ZH', ])
                translated_text = translated_texts['ZH'].replace('\r', '').replace('\n', '').replace('\r\n', '')
            except Exception as e:
                print(f">>> 翻译作品标题失败: {e}")

            # Caption for the photo
            formatted_date = run_date.replace("-", "")
            split_star = []
            stars = film_detail.film_stars.replace("-", "")
            if '----' in film_detail.film_stars:
                split_star = ['']
            else:
                split_star = film_detail.film_stars.split(" ")
                if len(split_star) >= 3:
                    split_star = split_star[:3]
                split_star = [f'\#{i}' for i in split_star]
            dvd_id = utils.convert_cid2code(film_detail.film_code)
            # tg markdownv2 不支持字符串中有- 所以要转义,tg caption 不支持-，
            # 所以设置为去掉
            dvd_id2 = dvd_id.replace("-", "")
            caption = (f"番号: `{dvd_id}`, 演员: `{stars}`\n"
                       f"标题: `{film_title}`\n"
                       f"{translated_text}\n"
                       f"\#D{formatted_date} \#{dvd_id2} {' '.join(split_star)}")

            suffix = '#query#jump'
            # URLs for the buttons
            url1 = f'https://Missav.com/search/{film_detail.film_code}'
            url2 = f'https://www5.Javmost.com/search/{film_detail.film_code}'
            url3 = f'https://Jable.tv/search/{film_detail.film_code}'
            url4 = f'https://netflav5.com/search?type=title&keyword={film_detail.film_code}'

            url5 = f'{item.telegraph_post_url}'
            # https://Missav.com/search/%s#query#jump
            # https://www5.Javmost.com/search/%s/#query#jump

            # Create an InlineKeyboardMarkup with two buttons
            keyboard = [
                [InlineKeyboardButton("MissAV观看", url=url1),
                 InlineKeyboardButton("JavMost观看", url=url2),
                 InlineKeyboardButton("JableTV观看", url=url3)
                 ],

                [InlineKeyboardButton("Netflav观看", url=url4),
                 InlineKeyboardButton("Telegraph查看明细", url=url5)],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            try:
                # Send the photo with the caption and buttons
                await bot.send_photo(chat_id=CHAT_ID, photo=photo_path, caption=caption, reply_markup=reply_markup,
                                     parse_mode='MarkdownV2', read_timeout=60 * 60, write_timeout=60 * 60,
                                     connect_timeout=60 * 60)
            except Exception as e:
                print(f"推送到频道失败: {e}")
                continue
            await asyncio.sleep(3)
            film_detail.has_push_channel = True
            try:
                database.session.commit()
            except Exception as e:
                print(f"更新记录失败: {e}")
                database.session.rollback()
            print(f">>> Telegram Patch 频道推送任务已完成")


if __name__ == '__main__':
    # asyncio.run(send_message2bot("你好"))
    asyncio.run(push_telegram_channel("2002-09-22"))
