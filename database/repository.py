import datetime

from psycopg2 import errors
from sqlalchemy import create_engine, exc, Engine
from sqlalchemy.orm import sessionmaker
from database.structure import Pos, Users, Words, UsersWords


class DBRepository:

    def __init__(self, dbname: str, user: str, password: str,
                 host='localhost', port='5432'):

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

    def add_pos(self, pos_name: str) -> None:

        """
        Добавляет новую часть речи в таблицу pos.

        Вводный параметр:
        - pos_name: наименование новой части речи
        """

        engine = self.get_engine()
        session_class = sessionmaker(bind=engine)
        session = session_class()

        existing_pos = session.query(Pos). \
            filter_by(pos_name=pos_name). \
            first()

        if not existing_pos:
            last_pos = session.query(Pos). \
                order_by(Pos.id.desc()). \
                first()

            if not last_pos:
                new_id = 1
            else:
                new_id = last_pos.id + 1

            new_pos = Pos(
                id=new_id,
                pos_name=pos_name
            )

            session.add(new_pos)
            session.commit()

        session.close()

    def update_pos(self, existing_pos_name: str,
                   new_pos_name: str) -> None:

        """
        Обновляет существующую часть речи в таблице pos.

        Вводные параметры:
        - existing_pos_name: наименование существующей части речи
        - existing_pos_name: новое наименование для существующей части речи
        """

        engine = self.get_engine()
        session_class = sessionmaker(bind=engine)
        session = session_class()

        existing_pos = session.query(Pos). \
            filter_by(pos_name=existing_pos_name). \
            first()

        new_pos = session.query(Pos). \
            filter_by(pos_name=new_pos_name). \
            first()

        if existing_pos and not new_pos:
            existing_pos.id = existing_pos.id
            existing_pos.pos_name = new_pos_name

            session.commit()

        session.close()

    def delete_pos(self, pos_name: str) -> None:

        """
        Удаляет часть речи из таблицы pos.

        Вводный параметр:
        - pos_name: наименование части речи, которую хотим удалить
        """

        engine = self.get_engine()
        session_class = sessionmaker(bind=engine)
        session = session_class()

        existing_pos = session.query(Pos). \
            filter_by(pos_name=pos_name). \
            first()

        if existing_pos:
            session.delete(existing_pos)
            session.commit()

        session.close()

    def get_pos(self) -> list[dict]:

        """
        Позволяет получить часть речи из таблицы pos.

        Выводной параметр:
        - список словарей, содержащий данные таблицы pos
        """

        engine = self.get_engine()
        session_class = sessionmaker(bind=engine)
        session = session_class()

        existing_pos = session.query(Pos).all()
        session.close()

        if existing_pos:
            pos_list = []
            for pos_item in existing_pos:
                pos_list.append({
                    'id': pos_item.id,
                    'pos_name': pos_item.pos_name
                })
            return pos_list
        else:
            return []

    def add_word(self, data_dict: dict,
                 is_added_by_users: bool) -> None:

        """
        Добавляет новое слово в таблицу words.

        Вводные параметры:
        - data_dict: словарь с данными английского слова
        - is_added_by_users: факт добавления слова пользователями
            -- True: слово добавлено пользователем
            -- False: слово добавлено разработчиком
        """

        pos_list = self.get_pos()
        pos_name = data_dict.get('pos_name')

        if pos_list:
            id_pos = []
            for pos_dict in pos_list:
                if pos_dict.get('pos_name') == pos_name:
                    id_pos.append(pos_dict.get('id'))

            if id_pos:
                id_pos = id_pos.pop()
                en_word = data_dict.get('en_word')
                en_trans = data_dict.get('en_trans')
                mp_3_url = data_dict.get('mp_3_url')
                ru_word = data_dict.get('ru_word')
                en_example = data_dict.get('en_example')
                ru_example = data_dict.get('ru_example')

                engine = self.get_engine()
                session_class = sessionmaker(bind=engine)
                session = session_class()

                existing_word = session.query(Words). \
                    filter_by(en_word=en_word, id_pos=id_pos). \
                    first()

                if not existing_word:
                    last_word = session.query(Words). \
                        order_by(Words.id.desc()). \
                        first()

                    if not last_word:
                        new_id = 1
                    else:
                        new_id = last_word.id + 1

                    new_word = Words(
                        id=new_id,
                        en_word=en_word,
                        en_trans=en_trans,
                        mp_3_url=mp_3_url,
                        id_pos=id_pos,
                        ru_word=ru_word,
                        en_example=en_example,
                        ru_example=ru_example,
                        is_added_by_users=is_added_by_users
                    )

                    session.add(new_word)
                    session.commit()

                else:
                    existing_word.en_trans = en_trans
                    existing_word.mp_3_url = mp_3_url
                    existing_word.ru_word = ru_word
                    existing_word.en_example = en_example
                    existing_word.ru_example = ru_example
                    existing_word.is_added_by_users = is_added_by_users
                    session.commit()

                session.close()

    def delete_word(self, data_dict: dict) -> None:

        """
        Удаляет слово из таблицы words.

        Вводный параметр:
        - data_dict: словарь с данными английского слова
        """

        pos_list = self.get_pos()
        pos_name = data_dict.get('pos_name')

        if pos_list:
            id_pos = []
            for pos_dict in pos_list:
                if pos_dict.get('pos_name') == pos_name:
                    id_pos.append(pos_dict.get('id'))

            if id_pos:
                id_pos = id_pos.pop()
                en_word = data_dict.get('en_word')

                engine = self.get_engine()
                session_class = sessionmaker(bind=engine)
                session = session_class()

                existing_word = session.query(Words). \
                    filter_by(en_word=en_word,
                              id_pos=id_pos). \
                    first()

                if existing_word:
                    session.delete(existing_word)
                    session.commit()

                session.close()

    def get_words(self, en_word: str = None,
                  is_added_by_users: bool = False) -> list[dict]:

        """
        Позволяет получить слова из таблицы words.
        По умолчанию выводятся все слова из данной таблицы.

        Вводные параметры:
        - en_word: слово, которое хотим получить методом фильтрации
        - is_added_by_users: факт добавления слова пользователями
            -- True: слово добавлено пользователем
            -- False: слово добавлено разработчиком

        Выводной параметр:
        - список словарей с данными английских слов
        """

        engine = self.get_engine()
        session_class = sessionmaker(bind=engine)
        session = session_class()

        if not en_word:
            existing_words = session.query(Words). \
                filter_by(is_added_by_users=is_added_by_users). \
                all()
        else:
            existing_words = session.query(Words). \
                filter_by(en_word=en_word,
                          is_added_by_users=is_added_by_users). \
                all()

        session.close()

        if existing_words:
            words_list = []
            for word_item in existing_words:
                words_list.append({
                    'id': word_item.id,
                    'en_word': word_item.en_word,
                    'en_trans': word_item.en_trans,
                    'mp_3_url': word_item.mp_3_url,
                    'id_pos': word_item.id_pos,
                    'ru_word': word_item.ru_word,
                    'en_example': word_item.en_example,
                    'ru_example': word_item.ru_example,
                    'is_added_by_users': word_item.is_added_by_users,
                })
            return words_list
        else:
            return []

    def add_user(self, user_dict: dict) -> None:

        """
        Добавляет нового пользователя в таблицу users.

        Вводный параметр:
        - user_dict: словарь с данными относительно пользователя
        """

        user_id = user_dict.get('user_id')
        first_name = user_dict.get('first_name')
        last_name = user_dict.get('last_name')
        username = user_dict.get('username')

        engine = self.get_engine()
        session_class = sessionmaker(bind=engine)
        session = session_class()

        existing_user = session.query(Users). \
            filter_by(user_id=user_id). \
            first()

        if not existing_user:
            new_user = Users(
                user_id=user_id,
                first_name=first_name,
                last_name=last_name,
                username=username
            )
            session.add(new_user)
            session.commit()

        else:
            existing_user.first_name = first_name
            existing_user.last_name = last_name
            existing_user.username = username
            session.commit()

        session.close()

    def delete_user(self, user_id: int) -> None:

        """
        Удаляет пользователя из таблицы users.

        Вводный параметр:
        - user_id: Telegram ID пользователя
        """

        engine = self.get_engine()
        session_class = sessionmaker(bind=engine)
        session = session_class()

        existing_user = session.query(Users). \
            filter_by(user_id=user_id). \
            first()

        if existing_user:
            session.delete(existing_user)
            session.commit()

        session.close()

    def get_users(self, user_id: int = None) -> list[dict]:

        """
        Позволяет получить информацию относительно
        пользователей приложения. По умолчанию
        выводятся все пользователи.

        Вводный параметр:
        - user_id: Telegram ID пользователя

        Выводной параметр:
        - список словарей с данными таблицы users
        """

        engine = self.get_engine()
        session_class = sessionmaker(bind=engine)
        session = session_class()

        if not user_id:
            existing_users = session.query(Users). \
                all()
        else:
            existing_users = session.query(Users). \
                filter_by(user_id=user_id). \
                all()

        session.close()

        if existing_users:
            users_list = []
            for user_item in existing_users:
                users_list.append({
                    'user_id': user_item.user_id,
                    'first_name': user_item.first_name,
                    'last_name': user_item.last_name,
                    'username': user_item.username
                })
            return users_list
        else:
            return []

    def prepare_user_word_pairs(self, user_id: int) -> None:

        """
        Позволяет связать пользователя со словами из
        csv-файла database.csv.

        Вводный параметр:
        - user_id: Telegram ID пользователя
        """

        word_data = self.get_words()
        user_data = self.get_users(user_id=user_id)

        words_id = []
        if word_data:
            for word_dict in word_data:
                words_id.append(word_dict.get('id'))

        user_id = 0
        if user_data:
            user_id += user_data.pop().get('user_id')

        engine = self.get_engine()
        session_class = sessionmaker(bind=engine)
        session = session_class()

        existing_user = session.query(UsersWords). \
            filter_by(user_id=user_id). \
            first()

        session.close()

        if not existing_user and words_id and user_id:

            engine = self.get_engine()
            session_class = sessionmaker(bind=engine)
            session = session_class()

            last_user_word_pair = session.query(UsersWords). \
                order_by(UsersWords.id.desc()). \
                first()

            session.close()

            if last_user_word_pair:
                idx_start = last_user_word_pair.id
            else:
                idx_start = 0

            object_list = []
            for idx, word_id in enumerate(words_id):
                object_list.append(
                    UsersWords(
                        id=idx_start + (idx + 1),
                        user_id=user_id,
                        word_id=word_id,
                        is_added=True,
                        is_user_word=False,
                        date_added=datetime.datetime.now(),
                        date_deleted=None
                    )
                )

            engine = self.get_engine()
            session_class = sessionmaker(bind=engine)
            session = session_class()

            try:
                session.bulk_save_objects(object_list)
                session.commit()
            except (exc.IntegrityError, errors.UniqueViolation) as e:
                pass

            session.close()

    def add_user_word(self, user_id: int,
                      data_dict: dict) -> None:

        """
        1. Добавляет новую пару "пользователь-слово"
           в таблицу users_words.
        2. Осуществляет добавление удаленного ранее слова
           (т.е. если ранее слово имело is_added=False,
           то после обработки появится is_added=True)

        Вводные параметры:
        - user_id: Telegram ID пользователя
        - data_dict: словарь с данными английского слова
        """

        word_data = self.get_words(en_word=data_dict.get('en_word'))
        user_data = self.get_users(user_id=user_id)

        if user_data:
            if not word_data:
                self.add_word(
                    data_dict,
                    is_added_by_users=True
                )
                word_data = self.get_words(
                    en_word=data_dict.get('en_word'),
                    is_added_by_users=True
                )

            words_id = []
            for dict_word in word_data:
                words_id.append(dict_word.get('id'))

            if words_id:

                engine = self.get_engine()
                session_class = sessionmaker(bind=engine)
                session = session_class()

                last_user_word_pair = session.query(UsersWords). \
                    order_by(UsersWords.id.desc()). \
                    first()

                session.close()

                if last_user_word_pair:
                    idx_start = last_user_word_pair.id
                else:
                    idx_start = 0

                object_list = []
                for idx, word_id in enumerate(words_id):
                    engine = self.get_engine()
                    session_class = sessionmaker(bind=engine)
                    session = session_class()

                    existing_word_user_pair = session.query(UsersWords). \
                        filter_by(user_id=user_id, word_id=word_id). \
                        first()

                    if not existing_word_user_pair:
                        object_list.append(
                            UsersWords(
                                id=idx_start + (idx + 1),
                                user_id=user_id,
                                word_id=word_id,
                                is_added=True,
                                is_user_word=True,
                                date_added=datetime.datetime.now(),
                                date_deleted=None
                            )
                        )

                    else:
                        if existing_word_user_pair.is_added is not True:
                            existing_word_user_pair.is_added = True
                            existing_word_user_pair.date_added = datetime.datetime.now()
                            existing_word_user_pair.date_deleted = None
                            session.commit()

                    session.close()

                if object_list:
                    engine = self.get_engine()
                    session_class = sessionmaker(bind=engine)
                    session = session_class()

                    try:
                        session.bulk_save_objects(object_list)
                        session.commit()
                    except (exc.IntegrityError, errors.UniqueViolation) as e:
                        pass

                    session.close()

    def remove_user_word(self, user_id: int,
                         en_word: str) -> None:

        """
        Делает неактивным слово из пары "пользователь-слово",
        расположенной внутри таблицы users_words.

        Вводные параметры:
        - user_id: Telegram ID пользователя
        - en_word: английское слово, которое не устроило пользователя
        """

        word_data1 = self.get_words(en_word, is_added_by_users=False)
        word_data2 = self.get_words(en_word, is_added_by_users=True)
        word_data = word_data1 + word_data2

        if word_data:
            for dict_data in word_data:
                word_id = dict_data.get('id')

                engine = self.get_engine()
                session_class = sessionmaker(bind=engine)
                session = session_class()

                existing_word_user_pair = session.query(UsersWords). \
                    filter_by(user_id=user_id, word_id=word_id, is_added=True). \
                    first()

                if existing_word_user_pair:
                    existing_word_user_pair.is_added = False
                    existing_word_user_pair.date_added = None
                    existing_word_user_pair.date_deleted = datetime.datetime.now()
                    session.commit()

                session.close()

    def delete_user_word_pair(self, user_id: int,
                              en_word: str) -> None:

        """
        Удаляет пару "пользователь-слово" из таблицы users_words.

        Вводные параметры:
        - user_id: Telegram ID пользователя
        - en_word: английское слово, требующее удаления из таблицы
                   users_words в рамках конкретного пользователя
        """

        word_data1 = self.get_words(en_word, is_added_by_users=False)
        word_data2 = self.get_words(en_word, is_added_by_users=True)
        word_data = word_data1 + word_data2

        if word_data:
            for dict_data in word_data:
                word_id = dict_data.get('id')

                engine = self.get_engine()
                session_class = sessionmaker(bind=engine)
                session = session_class()

                existing_word_user_pair = session.query(UsersWords). \
                    filter_by(user_id=user_id, word_id=word_id). \
                    first()

                if existing_word_user_pair:
                    session.delete(existing_word_user_pair)
                    session.commit()

                session.close()

    def get_user_words(self, user_id: int, pos_name: str = None) -> list[dict]:

        """
        Позволяет получить ВСЕ английские слова, находящиеся
        в базе данных пользователя и не имеющие is_added=False
        внутри таблицы users_words.

        Вводные параметры:
        - user_id: Telegram ID пользователя
        - pos_name: наименование части речи (по умолчанию None)

        Выводной параметр:
        - список словарей с данными таблицы users_words
        """

        engine = self.get_engine()
        session_class = sessionmaker(bind=engine)
        session = session_class()

        if pos_name is None:
            query_result = session.query(Words, Pos, UsersWords). \
                join(Pos, Pos.id == Words.id_pos). \
                join(UsersWords, UsersWords.word_id == Words.id). \
                filter(UsersWords.user_id == user_id,
                       UsersWords.is_added == True). \
                all()
        else:
            query_result = session.query(Words, Pos, UsersWords). \
                join(Pos, Pos.id == Words.id_pos). \
                join(UsersWords, UsersWords.word_id == Words.id). \
                filter(UsersWords.user_id == user_id,
                       UsersWords.is_added == True,
                       Pos.pos_name == pos_name). \
                all()

        session.close()

        if query_result:
            user_words_list = []
            for word, pos, _ in query_result:
                user_words_list.append({
                    'en_word': word.en_word,
                    'en_trans': word.en_trans,
                    'mp_3_url': word.mp_3_url,
                    'pos_name': pos.pos_name,
                    'ru_word': word.ru_word,
                    'en_example': word.en_example,
                    'ru_example': word.ru_example
                })
            return user_words_list
        else:
            return []

    def get_unique_user_words(self, user_id: int) -> list:

        """
        Выводит УНИКАЛЬНЫЕ английские слова пользователя.

        Вводный параметр:
        - user_id: Telegram ID пользователя

        Выводной параметр;
        - список с уникальными английскими словами пользователя
        """

        engine = self.get_engine()
        session_class = sessionmaker(bind=engine)
        session = session_class()

        query_result = session.query(Words, UsersWords). \
            join(UsersWords, UsersWords.word_id == Words.id). \
            filter(UsersWords.user_id == user_id,
                   UsersWords.is_added == True). \
            all()

        session.close()

        if query_result:
            word_id = []
            for _, word in query_result:
                word_id.append(word.id)

            engine = self.get_engine()
            session_class = sessionmaker(bind=engine)
            session = session_class()

            unique_english_words = session.query(Words.en_word). \
                filter(Words.id.in_(word_id)). \
                distinct(). \
                all()

            session.close()

            if unique_english_words:
                unique_words = []
                for word in unique_english_words:
                    unique_words.append(word.en_word)

                return unique_words
