import os

from dotenv import load_dotenv

from database.creation import DBCreation
from database.repository import DBRepository
from tgbot.connection import connect_telebot


def main_function(
    dbname: str, 
    user: str, 
    password: str, 
    host: str,
    port: str,
    token: str
) -> None:

    print('ПОДКЛЮЧЕНИЕ К БАЗЕ ДАННЫХ...')

    database = DBCreation(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )

    if not database.exists_db():
        database.create_db()
    
    if not database.exists_tables():
        database.create_tables()
        database.prepare_pos()
        database.prepare_words()

    repository = DBRepository(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )

    print('ПОДКЛЮЧЕНИЕ К ЧАТ-БОТУ...')

    connect_telebot(
        repository=repository,
        token=token
    )


if __name__ == '__main__':
    load_dotenv()
    main_function(
        dbname=os.getenv(key='DB_NAME'),
        user=os.getenv(key='DB_USER'),
        password=os.getenv(key='DB_PASSWORD'),
        host=os.getenv(key='HOST', default='localhost'),
        port=os.getenv(key='PORT', default='5432'),
        token=os.getenv(key='TG_TOKEN')
    )
