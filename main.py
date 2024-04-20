import asyncio

from sqlalchemy import desc

import crawl

import utils
import database
from database import DmmAvDaily, FilmDetailItem, FilmIntroItem

proxy_username = 'socks5-proxy-bomb'
proxy_password = 'socks5-proxy-bomb'
proxy_url = f'socks5://{proxy_username}:{proxy_password}@socks5-proxy-bomb.fly.dev:1080'


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
async def main():
    # 初始化基础db数据
    init_basic_db()
    # 批量查询出需要处理的url
    need_process_urls = database.session.query(DmmAvDaily).filter_by(has_run=False).limit(1).all()
    for dmm in need_process_urls:
        print(f"Fetching av daily data from: {dmm.fetch_url}")
        # 起始日期
        # url = "https://www.dmm.co.jp/digital/videoa/-/delivery-list/=/delivery_date=2002-06-14/"
        url2 = "https://www.dmm.co.jp/digital/videoa/-/detail/=/cid=baj013/"
        url3 = "https://www.dmm.co.jp/digital/videoa/-/detail/=/cid=sivr00336"

        # test code here
        resp = await crawl.fetch_data(url3, proxy_url=proxy_url)
        crawl.extract_film_detail_item(resp)

        # dmm_av_daily_resp = await crawl.fetch_data(dmm.fetch_url, proxy_url=proxy_url)
        # # print(dmm_av_daily_resp)
        # intro_item = crawl.extract_film_intro_item(dmm_av_daily_resp)
        #
        # pages = utils.get_max_page(dmm_av_daily_resp)
        # # print(pages)
        # if len(pages) > 1:
        #     pages = pages[1:]
        #     # print(pages)
        #     for page in pages:
        #         page_url = dmm.fetch_url + page + "/"
        #         dmm_av_daily_page_resp = await crawl.fetch_data(page_url, proxy_url=proxy_url)
        #         page_intro_item = crawl.extract_film_intro_item(dmm_av_daily_page_resp)
        #         intro_item.extend(page_intro_item)
        # # insert intro_item to database
        # print(intro_item)
        #
        # batch_inserts = []
        # for item in intro_item:
        #     film_intro = FilmIntroItem(
        #         film_title=item['film_title'],
        #         film_cover_url=item['film_cover_url'],
        #         film_detail_url=item['film_detail_url'],
        #         film_star=item['film_star'],
        #         film_price=item['film_price']
        #     )
        #     batch_inserts.append(film_intro)
        # try:
        #     database.session.add_all(batch_inserts)
        #     database.session.commit()
        #     print(f">>> Insert batch dmm av daily data successfully!")
        # except Exception as e:
        #     print(f">>> Error insert batch for dmm av daily data: {e}")
        #     database.session.rollback()
        # # TODO 爬取详情
        # for item in intro_item:
        #     detail_resp = await crawl.fetch_data(item['film_detail_url'], proxy_url=proxy_url)
        #     detail_dict = await crawl.extract_film_detail_item(detail_resp)
        #
        # # TODO 详情入库
        #
        # dmm.has_run = True
        # try:
        #     database.session.commit()
        #     print(f">>> 更新爬取任务记录成功,{dmm.run_date}任务完成!")
        # except Exception as e:
        #     print(f">>> 更新爬取任务记录失败: {e}")
        #     database.session.rollback()

# Run the asyncio event loop
if __name__ == "__main__":
    asyncio.run(main())
