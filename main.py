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
    url = "https://www.dmm.co.jp/digital/videoa/-/delivery-list/=/delivery_date=2002-06-14/"
    url2 = "https://www.dmm.co.jp/digital/videoa/-/detail/=/cid=baj013/"
    # response = await crawl.fetch_data(url, proxy_url=proxy_url)
    # print(response)

    # utils.get_max_page(response)
    # crawl.extract_film_intro_item(response)


# Run the asyncio event loop
if __name__ == "__main__":
    asyncio.run(main())
