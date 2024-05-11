import os
import re
import time
from typing import Optional

import requests
from bs4 import BeautifulSoup
from fake_headers import Headers

from filefinder import find_folder


class Parsing:

    def get_headers(self, os_: str, browser: str) -> dict:

        """
        Выводит фейковые заголовки пакета fake_headers.

        Вводные параметры:
        - os_: сокращенное название операционной системы
        - browser: название браузера

        Выводной параметр:
        - словарь-заголовок для работы с HTTP запросами
        """

        return Headers(os=os_, browser=browser).generate()

    def get_promt_soup(self, promt_url: str, en_word: str,
                       os_: str, browser: str, attempts: int,
                       error_timeout: int) -> Optional[BeautifulSoup]:

        """
        Выводит экземпляр класса BeautifulSoup.

        Вводные параметры:
        - promt_url: ссылка на сайт онлайн-словаря Promt
        - en_word: английское слово, которое хотим перевести в Promt
        - os_: сокращенное название операционной системы
        - browser: название браузера
        - attempts: кол-во попыток реализации get-запроса по URL-ссылке
        - error_timeout: кол-во секунд ожидания в случае неудачной попытки

        Выводной параметр:
        - soup: экземпляр класса BeautifulSoup (в случае удачного GET-запроса)
        """

        attempt_count = 0
        for _ in list(range(1, attempts + 1)):
            if attempts >= attempt_count:
                try:
                    resp = requests.get(
                        url=promt_url + en_word,
                        timeout=10,
                        headers=self.get_headers(os_, browser)
                    )
                    return BeautifulSoup(
                        markup=resp.content,
                        features="lxml"
                    )
                except (requests.exceptions.ConnectTimeout,
                        requests.exceptions.ReadTimeout,
                        requests.exceptions.ConnectionError):
                    print(f'requests.exceptions: {promt_url + en_word}')
                    time.sleep(error_timeout)
                    attempt_count += 1
            else:
                return None

    def parse_promt(self, soup: BeautifulSoup) -> dict:

        """
        Парсит сайт онлайн-словаря Promt.

        Вводный параметр:
        - soup: экземпляр класса BeautifulSoup

        Выводной параметр:
        - pos_dict: словарь с информацией о переведенном
                    слове в разрезе отдельных частей речи
        """

        pos_dict = {}
        for item in soup.findAll(name="div", attrs={"class": "cforms_result"}):
            for item2 in item.findAll(name="div", attrs={'translation-item'}):

                pos = item. \
                    find("span", attrs={"class": "ref_psp"}).text
                word = item2. \
                    find('span', attrs={'class': 'result_only sayWord'}).text

                try:
                    en_example = item2. \
                        find('div', attrs={'class': 'samSource'}).text
                    ru_example = item2. \
                        find('div', attrs={'class': 'samTranslation'}).text
                except AttributeError:
                    en_example, ru_example = None, None

                try:
                    trans = item. \
                        find('span', attrs={'class': 'transcription'}).text
                except AttributeError:
                    trans = None

                if pos not in pos_dict:
                    pos_dict[pos] = [{
                        'word': word,
                        'transcription': trans,
                        'en_example': en_example,
                        'ru_example': ru_example
                    }]
                else:
                    pos_dict[pos].append({
                        'word': word,
                        'transcription': trans,
                        'en_example': en_example,
                        'ru_example': ru_example
                    })

        return pos_dict

    def receive_promt_data(self, en_word: str, pos_list: list,
                           os_: str, browser: str,
                           attempts: int = 3,
                           error_timeout: int = 5) -> list[dict]:

        """
        Выводит перевод английского слова в разрезе отдельных частей речи.

        Вводные параметры:
        - en_word: английское слово, которое хотим перевести в Promt
        - pos_list: список учитываемых частей речи
        - os_: сокращенное название операционной системы
        - browser: название браузера
        - attempts: кол-во попыток реализации get-запроса по URL-ссылке
        - error_timeout: кол-во секунд ожидания в случае неудачной попытки

        Выводной параметр:
        - список словарей с информацией о переведенном слове в разрезе
        отдельных частей речи (в случае удачной реализации GET-запроса)
        """

        soup = self.get_promt_soup(
            promt_url='https://www.online-translator.com/translation/english-russian/',
            en_word=en_word,
            os_=os_,
            browser=browser,
            attempts=attempts,
            error_timeout=error_timeout
        )

        if not soup:
            dict_translation = None
        else:
            dict_translation = {en_word: self.parse_promt(soup)}

        word_data = []
        for pos in pos_list:

            try:
                dict_pos = dict_translation[en_word][pos][0]
            except KeyError:
                dict_pos = {}

            if dict_pos:
                word_data.append({
                    'en_word': en_word,
                    'ru_word': dict_pos.get('word'),
                    'en_trans': dict_pos.get('transcription'),
                    'pos_name': pos,
                    'en_example': dict_pos.get('en_example'),
                    'ru_example': dict_pos.get('ru_example'),
                })

        if word_data:
            return word_data
        else:
            return [{
                'en_word': en_word,
                'en_trans': '',
                'ru_word': None,
                'pos_name': 'unidentified',
                'en_example': 'No example',
                'ru_example': 'Пример отсутствует',
            }]

    def receive_oxford_data(self, en_word: str, os_: str,
                            browser: str) -> dict:

        """
        Выводит ссылку на MP3-файл с произношением
        английского слова. Ссылка парсится из онлайн-словаря Oxford.

        Вводные параметры:
        - en_word: английское слово, которое хотим найти
                   в онлайн-словаре Oxford
        - os_: сокращенное название операционной системы
        - browser: название браузера

        Выводной параметр:
        - словарь, содержащий ссылку на MP3-файл
        """

        oxford_url = f'https://www.oxfordlearnersdictionaries.com/definition/english/{en_word}'

        oxford_url_list = [
            oxford_url,
            oxford_url + "_1",
            oxford_url + "_2",
            oxford_url + "_3"
        ]

        for url in oxford_url_list:
            headers = self.get_headers(os_, browser)
            resp = requests.get(url, headers=headers)

            if 200 <= int(resp.status_code) < 300:
                soup = BeautifulSoup(
                    markup=resp.content,
                    features="lxml"
                )

                for item in soup.findAll(name="div", attrs={"class": "webtop"}):
                    try:
                        mp3_find = item.find(
                            name='div',
                            attrs={'class': 'pron-uk'}
                        )

                        mp_3_url = re.search(
                            pattern=r"mp3=(.+mp3.)",
                            string=str(mp3_find)
                        ).group(1)

                        mp_3_url = mp_3_url. \
                            replace('"', '')

                        if mp_3_url:
                            return {"mp_3_url": mp_3_url}

                    except AttributeError:
                        pass

        return {"mp_3_url": ''}

    def write_mp3(self, url: str, file_path: str,
                  os_: str, browser: str,
                  attempts: int,
                  error_timeout: int) -> bool:

        """
        Читает MP3-файл по URL-ссылке и
        записывает его по заданному пути.

        Вводные параметры:
        - url: URL-ссылка на MP3-файл
        - file_path: путь, по которому хотим записать файл
        - os_: сокращенное название операционной системы
        - browser: название браузера
        - attempts: кол-во попыток реализации get-запроса по URL-ссылке
        - error_timeout: кол-во секунд ожидания в случае неудачной попытки

        Выводной параметр:
        - bool: True - MP3-файл записан, False - наоборот
        """

        attempt_count = 0
        for _ in list(range(1, attempts + 1)):
            if attempts >= attempt_count:
                try:
                    resp = requests.get(
                        url=url,
                        headers=self.get_headers(os_, browser),
                        timeout=10
                    )
                    resp.raise_for_status()
                    with open(file_path, "wb") as file:
                        file.write(resp.content)
                    return True
                except (requests.exceptions.ConnectTimeout,
                        requests.exceptions.ReadTimeout,
                        requests.exceptions.ConnectionError):
                    print(f'requests.exceptions: {url}')
                    time.sleep(error_timeout)
            else:
                return False

    def write_user_mp3(self, en_word: str, mp_3_url: str,
                       transcription: str, os_: str,
                       browser: str) -> None:

        """
         1. Задает название MP3-файла с учетом наличия
         транскрипции у заданного английского слова.
         2. Создает путь, по которому будет записан MP3-файл
         3. Реализовывает запись файла через метод write_mp3
            (если он не существует внутри папки eng_audio_files_mp3)

        Вводные параметры:
        - en_word: английское слово
        - mp_3_url: ссылка на MP3-файл
        - transcription: транскрипция английского слова
        - os_: сокращенное название операционной системы
        - browser: название браузера
        """

        if mp_3_url:
            if transcription:
                mp3_path = os.path.join(
                    find_folder('eng_audio_files_mp3'),
                    f'{en_word} {transcription}.mp3'
                )
            else:
                mp3_path = os.path.join(
                    find_folder('eng_audio_files_mp3'),
                    f'{en_word[::-1].replace(" ", "", 1)[::-1]}.mp3'
                )

            if not os.path.exists(mp3_path):
                self.write_mp3(
                    url=mp_3_url,
                    file_path=mp3_path,
                    os_=os_,
                    browser=browser,
                    attempts=3,
                    error_timeout=10
                )

    def get_word_info(self, en_word: str, pos_list: list,
                      os_: str, browser: str) -> list[dict]:

        """
        Выводит обобщающую информацию об английском слове.

        Вводные параметры:
        - en_word: английское слово, которое хотим найти
                   в онлайн-словаре Oxford
        - pos_list: список учитываемых частей речи
        - os: сокращенное название операционной системы
        - browser: название браузера

        Выводной параметр:
        - список словарей с обобщающей информацией об
          английском слове в разрезе отдельных частей речи
        """

        promt_data = self.receive_promt_data(
            en_word=en_word,
            pos_list=pos_list,
            os_=os_,
            browser=browser
        )

        oxford_data = self.receive_oxford_data(
            en_word=en_word,
            os_=os_,
            browser=browser
        )

        word_list = []
        for idx, word_dict in enumerate(promt_data):
            if word_dict not in word_list:
                word_list.append(word_dict)
                word_list[idx].update(oxford_data)

        if len(word_list) > 1:
            for idx, word_dict in enumerate(word_list):
                if word_dict.get('ru_word') is None:
                    word_list.pop(idx)

        for word_dict in word_list:
            if word_dict.get('mp_3_url', None):
                self.write_user_mp3(
                    en_word=word_dict.get('en_word'),
                    mp_3_url=word_dict.get('mp_3_url'),
                    transcription=word_dict.get('en_trans'),
                    os_=os_,
                    browser=browser
                )
                break

        return word_list
