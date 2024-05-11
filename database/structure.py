import sys
import inspect

import sqlalchemy as sq
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Pos(Base):

    """
    pos - таблица с частями речи английских слов.

    Столбцы:
    - id: ID части речи
    - pos_name: название части речи
    """

    __tablename__ = 'pos'

    id = sq.Column(
        sq.Integer,
        primary_key=True
    )

    pos_name = sq.Column(
        sq.String(length=85),
        nullable=False,
        unique=True
    )


class Words(Base):

    """
    words - таблица с информацией английских слов.

    Столбцы:
    - id: ID английского слова
    - en_word: английское слово
    - en_trans: транскрипция английского слова
    - mp_3_url: URL-ссылка на MP3-файл с произношением слова
    - id_pos: ID части речи английского слова
    - ru_word: русский перевод английского слова
    - en_example: предожение с использованием английского слова
    - ru_example: предожение с использованием русского слова
    - is_added_by_users: параметр булева типа, отражающий
    добавление слова одним из пользователей (True - слово добавлено
    одним из пользователей, False - слово добавлено разработчиком)
    """

    __tablename__ = 'words'

    id = sq.Column(
        sq.Integer,
        primary_key=True
    )

    en_word = sq.Column(
        sq.String(length=350),
        nullable=False
    )

    en_trans = sq.Column(
        sq.String(length=350)
    )

    mp_3_url = sq.Column(
        sq.String(length=350)
    )

    id_pos = sq.Column(
        sq.Integer,
        sq.ForeignKey('pos.id'),
        nullable=False
    )

    ru_word = sq.Column(
        sq.String(length=350),
        nullable=False
    )

    en_example = sq.Column(
        sq.String(length=1500),
        nullable=False
    )

    ru_example = sq.Column(
        sq.String(length=1500),
        nullable=False
    )

    is_added_by_users = sq.Column(
        sq.Boolean(),
        nullable=False
    )


class Users(Base):

    """
    users - таблица с пользователями приложения.

    Столбцы:
    - user_id: ID пользователя в Telegram
    - first_name: имя пользователя
    - last_name: фамилия пользователя
    - username: профиль пользователя в Telegram
    """

    __tablename__ = 'users'

    user_id = sq.Column(
        sq.Integer,
        primary_key=True
    )

    first_name = sq.Column(
        sq.String(length=85),
        nullable=False
    )

    last_name = sq.Column(
        sq.String(length=85),
        nullable=False
    )

    username = sq.Column(
        sq.String(length=85),
        nullable=False,
        unique=True
    )


class UsersWords(Base):

    """
    users_words - таблица, связывающая
    пользователей со словами.

    Столбцы:
    - id: ID пары "пользователь-слово"
    - user_id: ID пользователя в Telegram
    - word_id: ID слова из таблицы words
    - is_added: параметр булева типа, отражающий добавление
    слова в личную БД пользователя (True - слово добавлено
    пользователем в личную БД, False - слово удалено из личной БД)
    - is_user_word: факт добавления слова пользователем
    (True - пользователь добавил слово, False -
    пользователь не имеет отношения к добавлению слова)
    - date_added: дата добавления пользователем слова
    - date_deleted: дата удаления пользователем слова
    """

    __tablename__ = 'users_words'

    id = sq.Column(
        sq.Integer,
        primary_key=True
    )

    user_id = sq.Column(
        sq.Integer,
        sq.ForeignKey('users.user_id',
                      ondelete='CASCADE'),
        nullable=False
    )

    word_id = sq.Column(
        sq.Integer,
        sq.ForeignKey('words.id'),
        nullable=False,
    )

    is_added = sq.Column(
        sq.Boolean,
        nullable=False
    )

    is_user_word = sq.Column(
        sq.Boolean,
        nullable=False
    )

    date_added = sq.Column(
        sq.DateTime
    )

    date_deleted = sq.Column(
        sq.DateTime
    )


def form_tables(engine: sq.Engine) -> None:

    """
    Создает таблицы с указанной выше структурой.
    """

    Base.metadata.create_all(engine)


def get_table_list() -> list:

    """
    Выводит список названий созданных таблиц.

    Выводной параметр:
    - список с названиями таблиц
    """

    table_list = []
    for table_name, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isclass(obj):
            if table_name != 'Base':
                table_list.append(getattr(obj, '__table__').name)
    return table_list
