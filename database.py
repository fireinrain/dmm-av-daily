import logging

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from sqlalchemy.orm import declarative_base

# logging.basicConfig()
# logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)

Base = declarative_base()


class TelegramInfo(Base):
    __tablename__ = 'telegram_info_detail'

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegraph_post_url = Column(String, nullable=False)
    film_detail_id = Column(Integer, nullable=False)
    has_create_post = Column(Boolean, default=False)
    has_push_channel = Column(Boolean, default=False)

    del_flag = Column(Boolean, default=False)
    create_time = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    update_time = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'), onupdate=datetime.now)


class DmmAvDaily(Base):
    __tablename__ = 'dmm_av_daily'

    id = Column(Integer, primary_key=True, autoincrement=True)
    # 访问url
    fetch_url = Column(String, nullable=False)
    # 是否已经运行
    has_run = Column(Boolean, default=False)
    # 运行日期
    run_date = Column(String, nullable=False)
    create_time = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    update_time = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'), onupdate=datetime.now)


# 作品简介
class FilmIntroItem(Base):
    __tablename__ = 'film_intro_item'

    id = Column(Integer, primary_key=True, autoincrement=True)
    # 标题
    film_title = Column(String, nullable=False)
    # 封面地址
    film_cover_url = Column(String, nullable=False)
    # 详情页地址
    film_detail_url = Column(String, nullable=False)
    # 主演
    film_star = Column(String, nullable=False)
    # 价格 日元
    film_price = Column(String, nullable=False)

    del_flag = Column(Boolean, default=False)
    create_time = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    update_time = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'), onupdate=datetime.now)


# 配信開始日：	2024/04/20
# 商品発売日：	2024/04/20
# 収録時間：	131分
# 出演者：	小宵こなん
# 監督：	濡れた子犬
# シリーズ：	S1 VR
# メーカー：	エスワン ナンバーワンスタイル
# レーベル：	S1 VR
# コンテンツタイプ：	3D
# ジャンル：	ハイクオリティVR  巨乳  痴女  騎乗位  パイズリ  独占配信  VR専用  単体作品  8KVR  主観
# 関連タグ  ：
#
# ベロキス VR 8K 痴女 乳首 痴女 淫語 ベロ キス ハイクオリティVR 8K 巨乳 VR 顔 舐め
# 品番：	sivr00336

# 配信开始日期：2024年04月20日
# 商品发售日期：2024年04月20日
# 收录时间：131分钟
# 出演者：小宵小南
# 导演：湿了的小狗
# 系列：S1 VR
# 制作商：S1 No.1 Style
# 品牌：S1 VR
# 内容类型：3D
# 类型：高质量VR 巨乳 痴女 骑乘位 乳交 独家配信 VR专用 单体作品 8KVR 第一人称视角
# 相关标签：
#
# 舌吻 VR 8K 痴女 乳头 痴女 淫话 舌 吻 高质量VR 8K 巨乳 VR 脸 舔
# 品号：sivr00336
class FilmDetailItem(Base):
    __tablename__ = 'film_detail_item'

    id = Column(Integer, primary_key=True, autoincrement=True)
    # 详情页地址
    film_detail_url = Column(String, nullable=False)
    # 作品缩略图
    film_pic_url = Column(String, nullable=False)
    # 作品海报
    film_poster_url = Column(String, nullable=False)
    # 作品标题
    film_title = Column(String, nullable=False)
    # 作品配信開始日
    film_publish_date = Column(String, nullable=False)
    # 上架日期
    film_sell_date = Column(String, nullable=False)
    # 时长
    film_length = Column(String, nullable=False)
    # 演员
    film_stars = Column(String, nullable=False)
    # 导演
    film_director = Column(String, nullable=False)
    # 系列
    film_series = Column(String, nullable=False)
    # 制作商
    film_producers = Column(String, nullable=False)
    # 品牌
    film_brand = Column(String, nullable=False)
    # 内容类型
    film_content_type = Column(String, nullable=False)
    # 类型
    film_type = Column(String, nullable=False)
    # 标签
    film_tags = Column(String, nullable=False)
    # 番号
    film_code = Column(String, nullable=False)
    # 作品内容简介
    film_desc = Column(String, nullable=False)
    # 作品样片图地址前缀
    film_sample_image_prefix = Column(String, nullable=False)
    # 作品样片图集合 格式 xxxx.jpg,abc.jpg
    film_sample_images = Column(String, nullable=False)

    del_flag = Column(Boolean, default=False)
    create_time = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    update_time = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'), onupdate=datetime.now)


# Example usage
engine = create_engine('sqlite:///dmm-av-daily.db', echo=True)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
