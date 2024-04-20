import asyncio

import crawl

import utils

proxy_username = 'socks5-proxy-bomb'
proxy_password = 'socks5-proxy-bomb'
proxy_url = f'socks5://{proxy_username}:{proxy_password}@socks5-proxy-bomb.fly.dev:1080'


# Example usage
async def main():
    # 起始日期
    url = "https://www.dmm.co.jp/digital/videoa/-/delivery-list/=/delivery_date=2002-06-14/"
    url2 = "https://www.dmm.co.jp/digital/videoa/-/detail/=/cid=baj013/"
    response = await crawl.fetch_data(url, proxy_url=proxy_url)
    print(response)

    utils.get_max_page(response)


# Run the asyncio event loop
if __name__ == "__main__":
    asyncio.run(main())
