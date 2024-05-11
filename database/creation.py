import csv

import sqlalchemy as sq
from psycopg2 import errors
from sqlalchemy import create_engine, exc, Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database

from filefinder import find_file
from database.structure import get_table_list, form_tables, Pos, Words


class DBCreation:

    def __init__(self, dbname: str, user: str, password: str,
                 host: str = 'localhost', port: str = '5432'):

        """
        Инициируемые параметры класса:
        - dbname: название базы данных
        - user: логин пользователя Postgres
        - password: пароль пользователя Postgres
        - host: хост (по умолчанию localhost)
        - port: порт (по умолчанию 5432)
        """

        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port

    def get_engine(self) -> Engine:

        """
        Запускает движок по DNS-ссылке. Запуск движка
        позволяет начать взаимодействие с БД через ORM.

        Выводной параметр:
        - движок sqlalchemy
        """

        dns_link = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}"
        return create_engine(dns_link)

    def exists_db(self) -> bool:

        """
        Проверяет существование БД.

        Выводной параметр:
        - bool: True - БД существует, False - БД отсутствует
        """

        engine = self.get_engine()
        if not database_exists(engine.url):
            return False
        else:
            return True

    def create_db(self) -> None:

        """
        Создает БД в случае ее отсутствия.
        """

        engine = self.get_engine()
        if not self.exists_db():
            create_database(engine.url)

    def exists_tables(self) -> bool:

        """
        Проверяет существование всех заданных таблиц в БД.

        Выводной параметр:
        - bool: True - все таблицы существуют в БД,
                False - не все таблицы существуют в БД
        """

        engine = self.get_engine()
        table_list = get_table_list()
        for table_name in table_list:
            if not sq.inspect(engine).has_table(table_name):
                return False
        return True

    def create_tables(self) -> None:

        """
        Создает таблицы в БД в случае их отсутствия.
        """

        engine = self.get_engine()
        if not self.exists_tables():
            form_tables(engine)

    def prepare_pos(self) -> None:

        """
        Заполняет таблицу pos.
        """

        engine = self.get_engine()
        session_class = sessionmaker(bind=engine)
        session = session_class()

        pos_count = session.query(Pos).count()

        if pos_count == 0:
            noun = Pos(id=1, pos_name='noun')
            verb = Pos(id=2, pos_name='verb')
            adjective = Pos(id=3, pos_name='adjective')
            unidentified = Pos(id=4, pos_name='unidentified')

            session.add_all([noun, verb, adjective,
                             unidentified])
            session.commit()

        session.close()

    def get_pos(self) -> list[dict]:

        """
        Выводит данные, содержащиеся в таблице pos.

        Выводной параметр:
        - список словарей с данными по частям речи
        """

        engine = self.get_engine()
        session_class = sessionmaker(bind=engine)
        session = session_class()

        existing_pos = session.query(Pos).all()

        pos_list = []
        if existing_pos:
            for pos_item in existing_pos:
                pos_list.append({
                    'id': pos_item.id,
                    'pos_name': pos_item.pos_name
                })
            return pos_list

    def prepare_words(self) -> None:

        """
        Заполняет таблицу words словами,
        содержащимися в csv-файле database.csv.
        """

        csv_path = find_file(file_name='database.csv')

        with (open(csv_path) as f):
            csv_reader = csv.reader(f)
            data = list(csv_reader)

        self.prepare_pos()
        pos_data = self.get_pos()

        object_list = []

        if pos_data:
            for idx, word_dict in enumerate(data[1:]):

                id_pos = []
                for pos_dict in pos_data:
                    if pos_dict.get('pos_name') == word_dict[1]:
                        id_pos.append(pos_dict.get('id'))

                object_list.append(
                    Words(
                        id=idx + 1,
                        en_word=word_dict[0],
                        en_trans=word_dict[5],
                        mp_3_url=word_dict[3],
                        id_pos=id_pos.pop(),
                        ru_word=word_dict[4],
                        en_example=word_dict[6],
                        ru_example=word_dict[7],
                        is_added_by_users=False
                    )
                )

            engine = self.get_engine()
            session_class = sessionmaker(bind=engine)
            session = session_class()

            try:
                session.bulk_save_objects(object_list)
                session.commit()
            except (exc.IntegrityError,
                    errors.UniqueViolation):
                pass

            session.close()
