import os
from dotenv import load_dotenv

from database.creation import DBCreation
from database.repository import DBRepository
from tgbot.connection import connect_telebot


def preload_common_audio_files():
    """Предварительная загрузка аудиофайлов для common words"""
    from tgbot.parsing import Parsing
    import os
    import re
    
    print("ПРЕДВАРИТЕЛЬНАЯ ЗАГРУЗКА АУДИОФАЙЛОВ...")
    
    parsing = Parsing()
    common_words = ['test', 'hello', 'world', 'time', 'people', 'water', 'food', 'house', 'car', 'book']
    
    for word in common_words:
        try:
            oxford_data = parsing.receive_oxford_data(
                en_word=word,
                os_='win',
                browser='chrome'
            )
            
            if oxford_data.get('mp_3_url'):
                parsing.write_user_mp3(
                    en_word=word,
                    mp_3_url=oxford_data.get('mp_3_url'),
                    transcription='',
                    os_='win',
                    browser='chrome'
                )
        except Exception as e:
            print(f"Ошибка при загрузке аудио для {word}: {e}")
    
    print("ПРЕДВАРИТЕЛЬНАЯ ЗАГРУЗКА ЗАВЕРШЕНА")

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

    # Просто создаем таблицы, если они не существуют
    if not database.exists_tables():
        database.create_tables()
        database.prepare_pos()
        database.prepare_words()

    # Создаем репозиторий для проверки данных
    repository = DBRepository(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )

    # Проверяем, есть ли данные в таблицах
    pos_data = repository.get_pos()
    if not pos_data or len(pos_data) == 0:
        database.prepare_pos()
    
    word_data = repository.get_words()
    if not word_data or len(word_data) == 0:
        database.prepare_words()

    # Предварительная загрузка аудиофайлов
    preload_common_audio_files()

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
