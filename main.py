import asyncio
import os
import sys

from sqlalchemy import desc, asc

import crawl
import telegraph_api
import tgbot

import utils
import database
from database import DmmAvDaily, FilmDetailItem, FilmIntroItem

SOCKS5_PROXY_URL = None
socks5_proxy_url = os.getenv('SOCKS5_PROXY_URL')
if socks5_proxy_url:
    SOCKS5_PROXY_URL = socks5_proxy_url
else:
    print(f"you must provide a socks5 proxy url like: `socks5://username:pass@host:port`!")


def init_basic_db():
    latest_record = database.session.query(DmmAvDaily).order_by(desc(DmmAvDaily.id)).first()
    if latest_record is None:
        print(f"Empty database,initial DB...")
        date_list = utils.generate_date_list()
        for date in date_list:
            fetch_url = f'https://www.dmm.co.jp/digital/videoa/-/delivery-list/=/delivery_date={date}/'
            daily = DmmAvDaily(fetch_url=fetch_url, run_date=date)
            try:
                database.session.add(daily)
                database.session.commit()
                print(f">>> Insert new dmm av daily data successfully!")
            except Exception as e:
                print(f">>> Error creating new record for dmm av daily data: {daily}")
                database.session.rollback()
    else:
        print(f"The latest record is: {latest_record.fetch_url},run status: {latest_record.has_run}")
        generate_date_list = utils.generate_date_list(latest_record.run_date)
        for date in generate_date_list:
            if date == latest_record.run_date:
                continue
            fetch_url = f'https://www.dmm.co.jp/digital/videoa/-/delivery-list/=/delivery_date={date}/'
            daily = DmmAvDaily(fetch_url=fetch_url, run_date=date)
            try:
                database.session.add(daily)
                database.session.commit()
                print(f">>> Insert new dmm av daily data successfully!")
            except Exception as e:
                print(f">>> Error creating new record for dmm av daily data: {daily}")
                database.session.rollback()


# Example usage
async def store_dmm_data_job():
    # 初始化基础db数据
    init_basic_db()
    # 批量查询出需要处理的url
    need_process_urls = database.session.query(DmmAvDaily).filter_by(has_run=False).limit(14).all()
    for dmm in need_process_urls:
        print(f"Fetching av daily data from: {dmm.fetch_url}")
        # 起始日期
        # url = "https://www.dmm.co.jp/digital/videoa/-/delivery-list/=/delivery_date=2002-06-14/"
        # url2 = "https://www.dmm.co.jp/digital/videoa/-/detail/=/cid=baj013/"
        # url3 = "https://www.dmm.co.jp/digital/videoa/-/detail/=/cid=sivr00336"
        # test code here
        # resp = await crawl.fetch_data(url3, proxy_url=proxy_url)
        # crawl.extract_film_detail_item(resp)

        dmm_av_daily_resp = await crawl.fetch_data(dmm.fetch_url, proxy_url=SOCKS5_PROXY_URL)
        # print(dmm_av_daily_resp)
        intro_item = crawl.extract_film_intro_item(dmm_av_daily_resp)

        pages = utils.get_max_page(dmm_av_daily_resp)
        # print(pages)
        if len(pages) > 1:
            pages = pages[1:]
            # print(pages)
            for page in pages:
                page_url = dmm.fetch_url + page + "/"
                dmm_av_daily_page_resp = await crawl.fetch_data(page_url, proxy_url=SOCKS5_PROXY_URL)
                page_intro_item = crawl.extract_film_intro_item(dmm_av_daily_page_resp)
                intro_item.extend(page_intro_item)
        # insert intro_item to database
        print(intro_item)

        batch_inserts = []
        for item in intro_item:
            film_intro = FilmIntroItem(
                film_title=item['film_title'],
                film_cover_url=item['film_cover_url'],
                film_detail_url=item['film_detail_url'],
                film_star=item['film_star'],
                film_price=item['film_price']
            )
            batch_inserts.append(film_intro)
        try:
            database.session.add_all(batch_inserts)
            database.session.commit()
            print(f">>> Insert batch dmm av daily data successfully!")
        except Exception as e:
            print(f">>> Error insert batch for dmm av daily data: {e}")
            database.session.rollback()
        # 爬取详情
        for item in intro_item:
            detail_resp = await crawl.fetch_data(item['film_detail_url'], proxy_url=SOCKS5_PROXY_URL)
            detail_dict = crawl.extract_film_detail_item(item['film_detail_url'], detail_resp)
            film_detail = FilmDetailItem(
                film_detail_url=detail_dict['film_detail_url'],
                film_pic_url=detail_dict['film_pic_url'],
                # 作品海报
                film_poster_url=detail_dict['film_poster_url'],
                # 作品标题
                film_title=detail_dict['film_title'],
                # 作品配信開始日
                film_publish_date=detail_dict['film_publish_date'],
                # 上架日期
                film_sell_date=detail_dict['film_sell_date'],
                # 时长
                film_length=detail_dict['film_length'],
                # 演员
                film_stars=detail_dict['film_stars'],
                # 导演
                film_director=detail_dict['film_director'],
                # 系列
                film_series=detail_dict['film_series'],
                # 制作商
                film_producers=detail_dict['film_producers'],
                # 品牌
                film_brand=detail_dict['film_brand'],
                # 内容类型
                film_content_type=detail_dict['film_content_type'],
                # 类型
                film_type=detail_dict['film_type'],
                # 标签
                film_tags=detail_dict['film_tags'],
                # 番号
                film_code=detail_dict['film_code'],
                # 作品内容简介
                film_desc=detail_dict['film_desc'],
                # 作品样片图地址前缀
                film_sample_image_prefix=detail_dict['film_sample_image_prefix'],
                # 作品样片图集合 格式 xxxx.jpg,abc.jpg
                film_sample_images=detail_dict['film_sample_images'],
            )
            # 详情入库
            try:
                database.session.add(film_detail)
                database.session.commit()
                print(f">>> Insert dmm av detail data successfully!")
            except Exception as e:
                print(f">>> Error insert for dmm av detail  data: {e}")
                database.session.rollback()
            await asyncio.sleep(1)

        dmm.has_run = True
        try:
            database.session.commit()
            print(f">>> 更新爬取任务记录成功,{dmm.run_date}任务完成!")
        except Exception as e:
            print(f">>> 更新爬取任务记录失败: {e}")
            database.session.rollback()

        await telegraph_api.create_telegraph_post(dmm.run_date)
        print(f">>> 创建Telegraph Post任务完成!")
        print(f">>> 存储DMM AV 信息任务完成!")


# async def create_telegraph_post_job():
#     # 创建telegraph post
#     need_process_urls = database.session.query(DmmAvDaily).filter_by(has_run=True).order_by(desc(DmmAvDaily.id)).limit(
#         1).all()
#     for dmm in need_process_urls:
#         await telegraph_api.create_telegraph_post(dmm.run_date)
#     print(f">>> 创建Telegraph Post任务完成!")


async def push_infos2telegram_channel_job():
    # 推送tg bot消息到频道
    need_process_urls = database.session.query(DmmAvDaily).filter_by(has_run=True).order_by(asc(DmmAvDaily.id)).limit(
        14).all()
    for dmm in need_process_urls:
        await tgbot.push_telegram_channel(dmm.run_date)
    print(f">>> 推送信息到Telegram Channel完成!")


async def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <argument>")
        sys.exit(1)

    argument = sys.argv[1]

    if argument == "store":
        await store_dmm_data_job()
    # elif argument == "create":
    #     await create_telegraph_post_job()
    elif argument == "push":
        await push_infos2telegram_channel_job()
        await tgbot.patch_tg_channel_push()
    elif argument == "patch":
        await telegraph_api.patch_info2telegraph()
        await tgbot.patch_tg_channel_push()
    else:
        print(f"Invalid argument: {argument}")
        sys.exit(1)


# Run the asyncio event loop
if __name__ == "__main__":
    # https://www.dmm.co.jp/digital/videoa/-/delivery-list/=/delivery_date=2002-06-14/
    # https://www.dmm.co.jp/digital/videoa/-/delivery-list/=/delivery_date=2002-06-16/
    # 测试连接
    asyncio.run(main())
    # need_process_urls = database.session.query(DmmAvDaily).filter_by(has_run=True).order_by(asc(DmmAvDaily.id)).limit(14).all()
    # print(need_process_urls)
