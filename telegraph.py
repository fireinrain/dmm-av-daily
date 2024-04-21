import database


async def create_telegraph_post(run_date: str):
    date_all = database.session.query(database.FilmDetailItem).filter_by(film_publish_date=run_date).all()
    pass


if __name__ == '__main__':
    pass