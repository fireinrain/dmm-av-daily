import asyncio

import aiohttp
from aiohttp_socks import ProxyType, ProxyConnector, ChainProxyConnector
from bs4 import BeautifulSoup


# fetch response from a url
async def fetch_data(url: str, proxy_url: str = "") -> str:
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh,en;q=0.9,zh-TW;q=0.8,zh-CN;q=0.7,ja;q=0.6",
        "Cache-Control": "no-cache",
        "Cookie": "cklg=ja; top_dummy=7d0bb44c-71c7-4d24-9840-6878d191e516; is_intarnal=true; "
                  "top_pv_uid=a4bfcb8e-591c-41b6-be9c-8c47ef8d190e; adpf_uid=fRCyNKaTmsLGsZFP; "
                  "rieSh3Ee_ga=GA1.1.2011002258.1705839031; _gcl_au=1.1.1979254774.1705839031; "
                  "i3_ab=61be2d49-4b90-45e1-a566-d9d7b36e903d; "
                  "_yjsu_yjad=1705839031.5863e2b3-e70b-4e3a-a328-ee04d43bf5ab; _dga=GA1.3.2011002258.1705839031; "
                  "_ga=GA1.3.25652193.1705839033; __lt__cid=ae9f3aa8-9226-41b0-8168-f70c4ce3b491; "
                  "_tt_enable_cookie=1; _ttp=A1cnwW15fOlEYHr1y5c_XEvM8nt; guest_id=VFkADgBEB1tbHUNJ; "
                  "book_block_popup_session=%7B%22coupon_41%22%3A1%2C%22okukore_20240119_0121_cojp%22%3A1%7D; "
                  "dmm_service=BFsBAx1FWwQCR1JXXlsJWUNeVwwBAx9KWFYNREEKRURHWkMDUQxDQFkLWlFdUUQMHBg_; "
                  "LSS_SESID=A1lRXE9CCQJYQTR6d0cKEF9WAFkQOzZJAWUICSQlcycjKhQ%2BXXt"
                  "%2BCSMiIHJkRwoQX1EOQWE1JWJtFl1YX1UEW1RQWlQEAAsKEVlYCREpYjA6N3EweyVGC1gOVQseFwhbWEEOB0dFbEINERURCBYLVF9GRgJcCg1eXhZdQl9TCEAGCgUPQFBfE1kQWwQJR0MCCw9dDVVDX0MDAFwTEw1XFUBYEVwECxETWR4c; list_condition=%7B%22digital%22%3A%7B%22limit%22%3Anull%2C%22sort%22%3Anull%2C%22view%22%3Anull%7D%7D; age_check_done=1; rieSh3Ee_ga_KQYE0DE5JW=GS1.1.1713083314.13.1.1713083391.0.0.2011816921; ckcy=1; mbox=check#true#1713609951|session#1713609890024-797072#1713611751; _dd_s=logs=1&id=005b69d9-2b95-40d1-b850-5f4d58a5e4c4&created=1713609890662&expire=1713610798763",
        "Pragma": "no-cache",
        "Priority": "u=0, i",
        "Sec-Ch-Ua": "\"Chromium\";v=\"124\", \"Google Chrome\";v=\"124\", \"Not-A.Brand\";v=\"99\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "\"macOS\"",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    }
    if proxy_url:
        connector = ProxyConnector.from_url(proxy_url)
        # Define the proxy credentials
        # Create an aiohttp session with a SOCKS5 proxy that requires authentication
        async with aiohttp.ClientSession(connector=connector) as session:
            try:
                # Use the session to perform HTTP requests with SOCKS5 proxy
                async with session.get(url, headers=headers) as response:
                    # Check if the request was successful
                    if response.status == 200:
                        # Read and return the response text
                        return await response.text()
                    else:
                        return f"Error: {response.status}"
            except Exception as e:
                return f"Error: request failed: {e}"
    async with aiohttp.ClientSession() as session:
        try:
            # Use the session to perform HTTP requests with SOCKS5 proxy
            async with session.get(url, headers=headers) as response:
                # Check if the request was successful
                if response.status == 200:
                    # Read and return the response text
                    return await response.text()
                else:
                    return f"Error: {response.status}"
        except Exception as e:
            return f"Error: request failed: {e}"


def extract_film_intro_item(html_content: str) -> list:
    result = []
    soup = BeautifulSoup(html_content, 'html.parser')
    items = soup.select('#list > li > div')
    for i in items:
        # print(i.text)
        film_detail_url = ""
        try:
            atag = i.select_one("p > a")
            film_detail_url = atag.attrs['href']
        except Exception as e:
            print(f"Exception on finding detail url:{e}")
            pass
        cover_img_url = ""
        try:
            img_tag = i.select_one("p > a > span > img")
            cover_img_url = img_tag.attrs['src']
        except Exception as e:
            print(f"Exception on finding cover:{e}")
            pass

        film_title = ""
        try:
            title_tag = i.select_one("p > a > span")
            span_next_tag = title_tag.find_next_sibling()
            film_title = span_next_tag.text
        except Exception as e:
            print(f"Exception on finding title:{e}")
            pass

        film_star = ""
        try:
            star_tag = i.select_one('.sublink > span > a')
            film_star = star_tag.text
        except Exception as e:
            print(f"Exception on finding star:{e}")

            pass

        film_price = ""
        try:
            price_tag = i.select_one('.value > p')
            price_next_tag = price_tag.find_next_sibling()
            film_price = price_next_tag.text.replace('円', '')
        except Exception as e:
            print(f"Exception on finding price:{e}")

            pass
        data = {}
        data['film_detail_url'] = film_detail_url
        data['film_cover_url'] = cover_img_url
        data['film_title'] = film_title
        data['film_star'] = film_star
        data['film_price'] = film_price
        result.append(data)
        # print("--------------------------------")
    return result


def extract_film_detail_item(film_detail_url: str, html_content: str) -> dict:
    result = {}
    result['film_detail_url'] = film_detail_url
    soup = BeautifulSoup(html_content, 'html.parser')

    film_poster_url = ""
    try:
        poster_tag = soup.select_one('#sample-video > a')
        film_poster_url = poster_tag.attrs['href']
    except Exception as e:
        print(f"Exception on finding poster url:{e}")

        pass
    result['film_poster_url'] = film_poster_url
    film_pic_url = ""
    try:
        small_poster_atg = soup.select_one('#sample-video > a > img')
        film_pic_url = small_poster_atg.attrs['src']
    except Exception as e:
        print(f"Exception on finding pic url:{e}")

        pass
    result['film_pic_url'] = film_pic_url
    # film_title = small_poster_atg.attrs['alt']
    film_title = ""
    try:
        film_title_tag = soup.select_one('#title')
        film_title = film_title_tag.text
    except Exception as e:
        print(f"Exception on finding  title:{e}")

        pass
    result['film_title'] = film_title
    # set default values
    result['support_device'] = ''
    result['film_publish_date'] = ''
    result['film_sell_date'] = ''
    result['film_length'] = ''
    result['film_stars'] = ''
    result['film_series'] = ''
    result['film_producers'] = ''
    result['film_brand'] = ''
    result['film_content_type'] = ''
    result['film_type'] = ''
    result['film_tags'] = ''
    result['film_code'] = ''
    result['film_director'] = ''
    data_tags = soup.select_one('table.mg-b20 > tr')
    if data_tags:
        for data_tag in data_tags:
            text = data_tag.text
            text = text.replace('\r', '').replace('\n', '').replace('\r\n', '')
            text = text.strip()
            if text == '':
                continue
            if '自動生成のため、関連度の低いタグが                    表示される場合があります。' in text:
                text = text.replace('自動生成のため、関連度の低いタグが                    表示される場合があります。',
                                    '')

            if text.startswith('VR対応デバイス'):
                support_device = text.split("：")[-1]
                result['support_device'] = support_device
                continue

            if text.startswith('配信開始日'):
                film_publish_date = text.split("：")[-1]
                result['film_publish_date'] = film_publish_date
                continue

            if text.startswith('商品発売日'):
                film_sell_date = text.split("：")[-1]
                result['film_sell_date'] = film_sell_date
                continue

            if text.startswith('収録時間'):
                film_length = text.split("：")[-1]
                result['film_length'] = film_length
                continue

            if text.startswith('出演者'):
                dats = data_tag.find_all('a')
                if len(dats) >= 2:
                    values = []
                    for i in dats:
                        dt = i.text
                        values.append(dt)
                    multi_value = ' '.join(values)
                    result['film_stars'] = multi_value
                else:
                    film_stars = text.split("：")[-1]
                    result['film_stars'] = film_stars
                continue

            if text.startswith('監督'):
                film_director = text.split("：")[-1]
                result['film_director'] = film_director
                continue
            else:
                result['film_director'] = ''

            if text.startswith('シリーズ'):
                film_series = text.split("：")[-1]
                result['film_series'] = film_series
                continue

            if text.startswith('メーカー'):
                film_producers = text.split("：")[-1]
                result['film_producers'] = film_producers
                continue

            if text.startswith('レーベル'):
                film_brand = text.split("：")[-1]
                result['film_brand'] = film_brand
                continue

            if text.startswith('コンテンツタイプ'):
                film_content_type = text.split("：")[-1]
                result['film_content_type'] = film_content_type
                continue

            if text.startswith('ジャンル'):
                film_type = text.split("：")[-1]
                result['film_type'] = film_type
                continue

            if text.startswith('関連タグ'):
                film_tags = text.split("：")[-1].strip()
                result['film_tags'] = film_tags
                continue

            if text.startswith('品番'):
                film_code = text.split("：")[-1].strip()
                result['film_code'] = film_code
                continue
            # print(text)
            # print("---")

    film_desc = ''
    try:
        desc_tag = soup.select_one('div.mg-b20.lh4')
        film_desc = desc_tag.text.strip()
    except Exception as e:
        print(f"Exception on finding desc:{e}")
        pass
    result['film_desc'] = film_desc

    # 样品图片地址
    film_sample_image_prefix = ''
    film_sample_images = ''
    try:
        sample_images_tag = soup.select_one('#sample-image-block')
        image_tags = sample_images_tag.select('a > img')
        tag0 = image_tags[0]
        link = tag0.attrs['src']
        # Find the last index of '/'
        last_slash_index = link.rfind('/')

        # Slice the string up to (and including) the last '/'
        film_sample_image_prefix = link[:last_slash_index + 1]
        image_names = []
        for image_tag in image_tags:
            href_ = image_tag.attrs['src']
            file_name = href_.split('/')[-1]
            image_names.append(file_name)
        film_sample_images = ','.join(image_names)
    except Exception as e:
        print(f"Exception on finding sample image:{e}")
        pass
    result['film_sample_image_prefix'] = film_sample_image_prefix
    result['film_sample_images'] = film_sample_images

    print(f"Extract detail data from: {film_poster_url} successfully!")
    print("----------------------------------------------------------------")
    return result


async def main():
    # data = await fetch_data('https://www.dmm.co.jp/digital/videoa/-/detail/=/cid=red150/',
    #                         'socks5://socks5-proxy-bomb:socks5-proxy-bomb@127.0.0.1:1080')
    # extract_film_detail_item('https://www.dmm.co.jp/digital/videoa/-/detail/=/cid=trl006/', data)

    # data2 = await fetch_data('https://www.dmm.co.jp/digital/videoa/-/delivery-list/=/delivery_date=2004-02-22/')
    # item = extract_film_intro_item(data2)

    data = await fetch_data('https://www.dmm.co.jp/digital/videoa/-/detail/=/cid=red150/')
    items = extract_film_detail_item('https://www.dmm.co.jp/digital/videoa/-/detail/=/cid=trl006/', data)

    print()


if __name__ == '__main__':
    asyncio.run(main())
