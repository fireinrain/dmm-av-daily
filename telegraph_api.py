import asyncio
import os

import database
import utils
from telegraph import AsyncTelegraph
from telegraph import AsyncUploadFile


async def create_telegraph_post(run_date: str):
    date_all = database.session.query(database.FilmDetailItem).filter_by(
        film_publish_date=run_date.replace("-", "/")).all()
    for item in date_all:
        first = database.session.query(database.TelegramInfo).filter_by(film_detail_id=item.id).first()
        if first is not None and first.has_create_post:
            continue
        # store record in database
        telegraph_info = database.TelegramInfo(
            telegraph_post_url="",
            film_detail_id=item.id
        )
        try:
            database.session.add(telegraph_info)
            database.session.commit()
            print(f">>> Insert telegraph info data successfully!")
        except Exception as e:
            print(f">>> Error insert for telegraph info data: {e}")
            database.session.rollback()
        # TODO 暂时跳过处理
        continue

        # upload pic to telegraph and store the url
        image_urls = []
        image_urls.append(item.film_poster_url)
        sample_urls = [item.film_sample_image_prefix + i for i in item.film_sample_images.split(",")]
        image_urls.extend(sample_urls)
        # 下载图片
        download_files = []
        for image_url in image_urls:
            file_name = utils.get_filename_from_url(image_url)
            download_file = await utils.download_file(image_url, "imgs" + os.sep + file_name)
            if download_file == "":
                continue
            download_files.append(download_file)
            await asyncio.sleep(0.05)
        # 上传到telegraph
        image_urls_on_telegraph = []
        try:
            image_urls_on_telegraph = await AsyncUploadFile(download_files)
            await asyncio.sleep(3)
        except Exception as e:
            print(f"样品图上传Telegraph 失败: {e}")

        tgph_post_url = ''
        async with AsyncTelegraph() as telegraph:
            await telegraph.create_account(short_name='dmm-av-daily')
            try:
                response = await telegraph.create_page(
                    f'{item.film_title}',
                    html_content=generate_html_content(item, image_urls_on_telegraph),
                    author_name='dmm-av-daily',
                    author_url='https://t.me/dmm_av'
                )
                tgph_post_url = response['url']

                print(f">>> Finish to post to Telegraph: {tgph_post_url}")
            except Exception as e:
                print(f"创建Telegraph post失败: {e}")
                continue
            # update telegraph post url to db
            telegraph_info.telegraph_post_url = tgph_post_url
            telegraph_info.has_create_post = True
            try:
                database.session.commit()
            except Exception as e:
                print(f"更新记录失败: {e}")
                database.session.rollback()
        # 清理图片下载缓存
        print(f">>> Clean Image download cache.")
        utils.clean_img_folder('imgs')


def generate_html_content(item: database.FilmDetailItem, image_urls: []) -> str:
    image_urls = ['https://' + i for i in image_urls]
    # print(image_urls)
    sample_images_tags = [f'<img src="{d}">' for i, d in enumerate(image_urls) if i != 0]
    sample_images_tags_str = ''.join(sample_images_tags)
    return (f'<img src="{image_urls[0]}">'
            f'<h4>作品元数据</h4>'
            f'<p>作品详情页: <a href="{item.film_detail_url}" target="_blank">{item.film_detail_url}</a></p>'
            f'<p>作品缩略图: {item.film_pic_url}</p>'
            f'<p>作品海报: {item.film_poster_url}</p>'
            f'<p>作品标题: {item.film_title}</p>'
            f'<p>作品配信開始日: {item.film_publish_date}</p>'
            f'<p>上架日期: {item.film_sell_date}</p>'
            f'<p>作品时长: {item.film_length}</p>'
            f'<p>演员: {item.film_stars}</p>'
            f'<p>导演: {item.film_director}</p>'
            f'<p>系列: {item.film_series}</p>'
            f'<p>制作商: {item.film_producers}</p>'
            f'<p>品牌: {item.film_brand}</p>'
            f'<p>内容类型: {item.film_content_type}</p>'
            f'<p>作品类型: {item.film_type}</p>'
            f'<p>作品标签: {item.film_tags}</p>'
            f'<p>识别码: {item.film_code}</p>'
            f'<p>内容简介: {item.film_desc}</p>'
            f'<h4>样品图片</h4>'
            f'{sample_images_tags_str}')


async def patch_info2telegraph():
    tginfos = database.session.query(database.TelegramInfo).filter_by(
        has_create_post=False).all()
    for info in tginfos:
        item_detail = database.session.query(database.FilmDetailItem).filter_by(id=info.film_detail_id).first()
        if item_detail is None:
            # store record in database
            telegraph_info = database.TelegramInfo(
                telegraph_post_url="",
                film_detail_id=item_detail.id
            )
            try:
                database.session.add(telegraph_info)
                database.session.commit()
                print(f">>> Insert telegraph info data successfully!")
            except Exception as e:
                print(f">>> Error insert for telegraph info data: {e}")
                database.session.rollback()

        # upload pic to telegraph and store the url
        image_urls = []
        image_urls.append(item_detail.film_poster_url)
        sample_urls = [item_detail.film_sample_image_prefix + i for i in item_detail.film_sample_images.split(",")]
        image_urls.extend(sample_urls)
        # 下载图片
        download_files = []
        for image_url in image_urls:
            file_name = utils.get_filename_from_url(image_url)
            download_file = await utils.download_file(image_url, "imgs" + os.sep + file_name)
            if download_file == "":
                continue
            download_files.append(download_file)
            await asyncio.sleep(0.05)
        # 上传到telegraph
        image_urls_on_telegraph = []
        try:
            image_urls_on_telegraph = await AsyncUploadFile(download_files)
            await asyncio.sleep(3)
        except Exception as e:
            print(f"样品图上传Telegraph 失败: {e}")

        tgph_post_url = ''
        async with AsyncTelegraph() as telegraph:
            await telegraph.create_account(short_name='dmm-av-daily')
            try:
                response = await telegraph.create_page(
                    f'{item_detail.film_title}',
                    html_content=generate_html_content(item_detail, image_urls_on_telegraph),
                    author_name='dmm-av-daily',
                    author_url='https://t.me/dmm_av'
                )
                tgph_post_url = response['url']

                print(f">>> Finish to post to Telegraph: {tgph_post_url}")
            except Exception as e:
                print(f"创建Telegraph post失败: {e}")
                continue
            # update telegraph post url to db
            info.telegraph_post_url = tgph_post_url
            info.has_create_post = True
            try:
                database.session.commit()
            except Exception as e:
                print(f"更新记录失败: {e}")
                database.session.rollback()
        # 清理图片下载缓存
        print(f">>> Clean Image download cache.")
        utils.clean_img_folder('imgs')


if __name__ == '__main__':
    asyncio.run(create_telegraph_post("2002-06-14"))
