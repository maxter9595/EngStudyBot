import os
import random

import pytest
from sqlalchemy import Engine
from dotenv import load_dotenv

from tgbot.parsing import Parsing
from database.creation import DBCreation
from database.structure import get_table_list
from database.repository import DBRepository
from tgbot.functionality import Functionality


load_dotenv()

TEST_DBNAME = os.getenv(key='TEST_DB_NAME')
USER = os.getenv(key='DB_USER')
PASSWORD = os.getenv(key='DB_PASSWORD')

POS_LIST = [
    'noun',
    'verb',
    'adjective'
]

TEST_WORD_DICT = {
    'en_word': 'test case',
    'en_trans': '[test keɪs]',
    'mp_3_url': 'https://www.oxfordlearnersdictionaries.com/media/english/us_pron/t/tes/test_/test_case_1_us_1.mp3',
    'pos_name': 'noun',
    'ru_word': 'прецедент',
    'en_example': 'This is a test case that will influence what other judges decide.',
    'ru_example': 'Это прецедент, который повлияет на решение других судей.'
}

TEST_USER_DICT = {
    'user_id': 101010101,
    'first_name': 'Тестовый',
    'last_name': 'Пользователь',
    'username': 'testuser'
}

TEST_URL = 'https://www.oxfordlearnersdictionaries.com/media/english/uk_pron/t/tes/test_/test__gb_1.mp3'


class Tests:

    def setup_method(self) -> None:
        self.test_database = DBCreation(
            dbname=TEST_DBNAME,
            user=USER,
            password=PASSWORD
        )
        self.test_repository = DBRepository(
            dbname=TEST_DBNAME,
            user=USER,
            password=PASSWORD
        )
        self.test_parsing = Parsing()
        self.test_functionality = Functionality()

    def teardown_method(self) -> None:
        del self.test_database
        del self.test_repository
        del self.test_parsing
        del self.test_functionality

    @pytest.mark.parametrize(
        'expected_bool',
        (True,)
    )
    def test_get_engine(self, expected_bool: bool) -> None:
        actual_bool1 = (
                Engine is type(self.test_database.get_engine())
        )
        actual_bool2 = (
                Engine is type(self.test_repository.get_engine())
        )
        assert actual_bool1 == expected_bool
        assert actual_bool2 == expected_bool

    @pytest.mark.parametrize(
        'expected_bool',
        (True,)
    )
    def test_create_db(self, expected_bool: bool) -> None:
        self.test_database.create_db()
        actual_bool = self.test_database.exists_db()
        assert actual_bool == expected_bool

    @pytest.mark.parametrize(
        'expected_bool',
        (True,)
    )
    def test_create_tables(self, expected_bool: bool) -> None:
        self.test_database.create_tables()
        actual_bool = self.test_database.exists_tables()
        assert actual_bool == expected_bool

    @pytest.mark.parametrize(
        'expected_min_len',
        (1,)
    )
    def test_prepare_pos(self, expected_min_len: int) -> None:
        self.test_database.prepare_pos()
        actual_len = len(
            self.test_database.get_pos()
        )
        assert actual_len >= expected_min_len

    @pytest.mark.parametrize(
        'expected_min_len',
        (4,)
    )
    def test_prepare_words(self, expected_min_len: int) -> None:
        self.test_database.prepare_words()
        actual_len = len(
            self.test_repository.get_words()
        )
        assert actual_len >= expected_min_len

    @pytest.mark.parametrize(
        'expected_min_len',
        (1,)
    )
    def test_get_table_list(self, expected_min_len: int) -> None:
        actual_len = len(
            get_table_list()
        )
        assert actual_len >= expected_min_len

    @pytest.mark.parametrize(
        'pos_name,expected_bool',
        (['new pos', True],)
    )
    def test_add_pos(self, pos_name: str,
                     expected_bool: bool) -> None:
        self.test_repository.add_pos(
            pos_name=pos_name
        )
        pos_data = self.test_repository.get_pos()
        if pos_data:
            last_pos_dict = pos_data.pop()
            actual_bool = (
                    last_pos_dict.get('pos_name') == pos_name
            )
            assert actual_bool == expected_bool

    @pytest.mark.parametrize(
        'pos_name,new_pos_name,expected_bool',
        (['new pos', 'new pos!', True],)
    )
    def test_update_pos(self, pos_name: str, new_pos_name: str,
                        expected_bool: bool):
        self.test_repository.update_pos(
            existing_pos_name=pos_name,
            new_pos_name=new_pos_name
        )
        pos_data = self.test_repository.get_pos()
        if pos_data:
            last_pos_dict = pos_data.pop()
            actual_bool = (
                    last_pos_dict.get('pos_name') == new_pos_name
            )
            assert actual_bool == expected_bool

    @pytest.mark.parametrize(
        'pos_name,expected_bool',
        (['new pos!', False],)
    )
    def test_delete_pos(self, pos_name: str,
                        expected_bool: bool) -> None:
        self.test_repository.delete_pos(
            pos_name=pos_name
        )
        pos_data = self.test_repository.get_pos()
        if pos_data:
            last_pos_dict = pos_data.pop()
            actual_bool = (
                    last_pos_dict.get('pos_name') == pos_name
                           )
            assert actual_bool == expected_bool

    @pytest.mark.parametrize(
        'expected_min_len',
        (1,)
    )
    def test_get_pos(self, expected_min_len: int) -> None:
        actual_len = len(self.test_database.get_pos())
        assert actual_len >= expected_min_len

    @pytest.mark.parametrize(
        'word_dict,expected_bool',
        ([TEST_WORD_DICT, True],)
    )
    def test_add_word(self, word_dict: dict,
                      expected_bool: bool) -> None:
        en_word = word_dict.get('en_word')
        self.test_repository.add_word(
            data_dict=word_dict,
            is_added_by_users=True
        )
        word_data = self.test_repository.get_words(
            en_word=en_word,
            is_added_by_users=True
        )
        if word_data:
            word_dict = word_data.pop()
            actual_bool = (
                    word_dict.get('en_word') == en_word
            )
            assert actual_bool == expected_bool

    @pytest.mark.parametrize(
        'word_dict,expected_bool',
        ([TEST_WORD_DICT, False],)
    )
    def test_delete_word(self, word_dict: dict,
                         expected_bool: bool) -> None:
        en_word = word_dict.get('en_word')
        self.test_repository.delete_word(
            data_dict=word_dict
        )
        word_data = self.test_repository.get_words(
            en_word=en_word,
            is_added_by_users=True
        )
        if word_data:
            word_dict = word_data.pop()
            actual_bool = (
                    word_dict.get('en_word') == en_word
            )
            assert actual_bool == expected_bool

    @pytest.mark.parametrize(
        'expected_min_len',
        (1,)
    )
    def test_get_words(self, expected_min_len: int) -> None:
        actual_len = len(
            self.test_repository.get_words()
        )
        assert actual_len >= expected_min_len

    @pytest.mark.parametrize(
        'user_dict,expected_bool',
        ([TEST_USER_DICT, True],)
    )
    def test_add_user(self, user_dict: dict,
                      expected_bool: bool) -> None:
        user_id = user_dict.get('user_id')
        self.test_repository.add_user(
            user_dict=user_dict
        )
        user_data = self.test_repository.get_users(
            user_id=user_id
        )
        if user_data:
            user_dict = user_data.pop()
            actual_bool = (user_dict.get('user_id') == user_id)
            assert actual_bool == expected_bool

    @pytest.mark.parametrize(
        'user_dict,expected_bool',
        ([TEST_USER_DICT, False],)
    )
    def test_delete_user(self, user_dict: dict,
                         expected_bool: bool) -> None:
        user_id = user_dict.get('user_id')
        self.test_repository.delete_user(
            user_id=user_id
        )
        user_data = self.test_repository.get_users(
            user_id=user_id
        )
        if user_data:
            user_dict = user_data.pop()
            actual_bool = (user_dict.get('user_id') == user_id)
            assert actual_bool == expected_bool

    @pytest.mark.parametrize(
        'user_dict,expected_min_len',
        ([TEST_USER_DICT, 1],)
    )
    def test_get_user(self, user_dict: dict,
                      expected_min_len: int) -> None:
        user_id = user_dict.get('user_id')
        self.test_repository.add_user(
            user_dict=user_dict
        )
        actual_len = len(
            self.test_repository.get_users(user_id)
        )
        assert actual_len >= expected_min_len

    @pytest.mark.parametrize(
        'user_dict,expected_min_len',
        ([TEST_USER_DICT, 4],)
    )
    def test_prepare_user_word_pairs(self, user_dict: dict,
                                     expected_min_len: int) -> None:
        user_id = user_dict.get('user_id')
        self.test_repository.prepare_user_word_pairs(
            user_id=user_id
        )
        actual_len = len(
            self.test_repository.get_user_words(user_id)
        )
        assert actual_len >= expected_min_len

    @pytest.mark.parametrize(
        'user_dict,word_dict,expected_bool',
        ([TEST_USER_DICT, TEST_WORD_DICT, True],)
    )
    def add_user_word(self, user_dict: dict, word_dict: dict,
                      expected_bool: bool) -> None:
        user_id = user_dict.get('user_id')
        en_word = word_dict.get('en_word')

        self.test_repository.add_user_word(
            user_id=user_id,
            data_dict=word_dict
        )
        unique_words = self.test_repository.get_unique_user_words(
            user_id=user_id
        )
        actual_bool = (
                en_word in unique_words
        )
        assert actual_bool == expected_bool

    @pytest.mark.parametrize(
        'user_dict,word_dict,expected_bool',
        ([TEST_USER_DICT, TEST_WORD_DICT, False],)
    )
    def remove_user_word_test(self, user_dict: dict,
                              word_dict: dict,
                              expected_bool: bool) -> None:
        user_id = user_dict.get('user_id')
        en_word = word_dict.get('en_word')
        self.test_repository.remove_user_word(
            user_id=user_id,
            en_word=en_word
        )
        unique_words = self.test_repository.get_unique_user_words(
            user_id=user_id
        )
        actual_bool = (
                en_word in unique_words
        )
        assert actual_bool == expected_bool

    @pytest.mark.parametrize(
        'user_dict,word_dict,expected_bool',
        ([TEST_USER_DICT, TEST_WORD_DICT, False],)
    )
    def delete_delete_user_word_pair(self, user_dict: dict,
                                     word_dict: dict,
                                     expected_bool: bool) -> None:
        user_id = user_dict.get('user_id')
        en_word = word_dict.get('en_word')
        self.test_repository.delete_user_word_pair(
            user_id=user_id,
            en_word=en_word
        )
        unique_words = self.test_repository.get_unique_user_words(
            user_id=user_id
        )
        actual_bool = (
                en_word in unique_words
        )
        assert actual_bool == expected_bool

    @pytest.mark.parametrize(
        'user_dict,expected_min_len',
        ([TEST_USER_DICT, 4],)
    )
    def test_get_user_words(self, user_dict: dict,
                            expected_min_len: int) -> None:
        user_id = user_dict.get('user_id')
        actual_len = len(
            self.test_repository.get_user_words(user_id)
        )
        assert actual_len >= expected_min_len

    @pytest.mark.parametrize(
        'user_dict,expected_min_len',
        ([TEST_USER_DICT, 4],)
    )
    def test_get_unique_user_words(self, user_dict: dict,
                                   expected_min_len: int) -> None:
        user_id = user_dict.get('user_id')
        actual_len = len(
            self.test_repository.get_unique_user_words(user_id)
        )
        assert actual_len >= expected_min_len

    @pytest.mark.parametrize(
        'os_,browser,expected_bool',
        (['win', 'chrome', True],)
    )
    def test_get_headers(self, os_: str, browser: str,
                         expected_bool: bool) -> None:
        test_header = self.test_parsing.get_headers(
            os_=os_,
            browser=browser
        )
        actual_bool = (
                'keep-alive' in test_header.get('Connection')
        )
        assert actual_bool == expected_bool

    @pytest.mark.parametrize(
        'en_word,pos_list,os_,browser,expected_translation,expected_bool',
        (['test', ['noun'], 'win', 'chrome', 'испытание', True],
         ['test', ['verb'], 'win', 'chrome', 'тестировать', True],
         ['test', ['adjective'], 'win', 'chrome', 'испытательный', True])
    )
    def test_receive_promt_data(self, en_word: str,
                                pos_list: list,
                                os_: str, browser: str,
                                expected_translation: str,
                                expected_bool: bool) -> None:

        word_data = self.test_parsing.receive_promt_data(
            en_word=en_word,
            pos_list=pos_list,
            os_=os_,
            browser=browser
        )
        if word_data:
            word_dict = word_data.pop(0)
            actual_bool = (
                    word_dict.get('ru_word') == expected_translation
            )
            assert actual_bool == expected_bool

    @pytest.mark.parametrize(
        'en_word,os_,browser,expected_mp3,expected_bool',
        (['test', 'win', 'chrome', TEST_URL, True],)
    )
    def test_receive_oxford_data(self, en_word: str,
                                 os_: str, browser: str,
                                 expected_mp3: str,
                                 expected_bool: bool) -> None:
        mp3_dict = self.test_parsing.receive_oxford_data(
            en_word=en_word,
            os_=os_,
            browser=browser
        )
        if mp3_dict:
            actual_bool = (
                    mp3_dict.get('mp_3_url') == expected_mp3
            )
            assert actual_bool == expected_bool

    @pytest.mark.parametrize(
        'en_word,pos_list,os_,browser,expected_translation,expected_bool',
        (['test', ['noun'], 'win', 'chrome', 'испытание', True],
         ['test', ['verb'], 'win', 'chrome', 'тестировать', True],
         ['test', ['adjective'], 'win', 'chrome', 'испытательный', True])
    )
    def test_get_word_info(self, en_word: str, pos_list: list,
                           os_: str, browser: str,
                           expected_translation: str,
                           expected_bool: bool) -> None:
        word_data = self.test_parsing.get_word_info(
            en_word=en_word,
            pos_list=pos_list,
            os_=os_,
            browser=browser
        )
        if word_data:
            word_dict = word_data.pop(0)
            actual_bool = (
                    word_dict.get('ru_word') == expected_translation
            )
            assert actual_bool == expected_bool

    @pytest.mark.parametrize(
        'word,eng_bool,expected_bool',
        (['test', True, True],
         ['тест', True, False],
         ['123456', True, False],
         ['тест', False, True],
         ['ёлка', False, True],
         ['test', False, False],
         ['123456', False, False])
    )
    def test_check_word_letters(self, word: str,
                                eng_bool: bool,
                                expected_bool: bool) -> None:
        actual_bool = self.test_functionality.check_word_letters(
            word=word,
            eng_bool=eng_bool
        )
        assert actual_bool == expected_bool

    @pytest.mark.parametrize(
        'user_dict,expected_bool',
        ([TEST_USER_DICT, True],)
    )
    def test_get_random_words(self, user_dict: dict,
                              expected_bool: bool) -> None:
        user_id = user_dict.get('user_id')
        pos_database = self.test_repository.get_user_words(
            user_id=user_id,
            pos_name=random.choice(POS_LIST)
        )
        (target_word, translate, others, _,
         _, _) = self.test_functionality.get_random_words(
            pos_database=pos_database
        )
        actual_bool = (
                (len(target_word) > 0) and
                (len(translate) > 0) and
                (len(others) > 0)
        )
        assert actual_bool == expected_bool
