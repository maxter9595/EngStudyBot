import csv
import time
from typing import Optional

import requests
from bs4 import BeautifulSoup

from data_formation.english_html import write_dir
from data_formation.english_html import get_headers


def launch_get_requests(attempts: int, error_timeout: int,
                        promt_link: str, my_word: str,
                        os: str, browser: str) -> Optional[BeautifulSoup]:
    """
    Запускает GET-запрос для парсинга онлайн-словаря PROMT.One.

    Вводные параметры:
    - attempts: количество попыток парсинга сайта
                в условиях наличия возможной ошибки
                requests.exceptions.ConnectTimeout.
    - error_timeout: количество секунд остановки функции,
                     после которых последует реализация
                     следующей попытки осуществления
                     GET-запроса.
    - promt_link: ссылка на онлайн-словарь PROMT.One.
    - my_word: слово, которое необходимо перевести.
    - os: название операционной системы в разрезе
          библиотеки fake_headers.
    - browser: название браузера в разрезе
               библиотеки fake_headers.

    Выводной параметр:
    - экземпляр класса BeautifulSoup
      (в случае успешного GET-запроса).
    """

    attempt_count = 0
    for _ in list(range(1, attempts + 1)):
        if attempts >= attempt_count:
            try:
                resp = requests.get(
                    url=promt_link + my_word,
                    timeout=10,
                    headers=get_headers(os_=os, browser=browser)
                )

                soup = BeautifulSoup(
                    markup=resp.content,
                    features="lxml"
                )
                return soup

            except (requests.exceptions.ConnectTimeout,
                    requests.exceptions.ReadTimeout,
                    requests.exceptions.ConnectionError):
                print('requests.exceptions: повторная попытка...')
                time.sleep(error_timeout)
                attempt_count += 1

        else:
            return None


def promt_site_parsing(soup: BeautifulSoup, my_word: str) -> dict:
    """
    Позволяет вытащить все необходимые данные
    из HTML-кода онлайн-словаря PROMT.One.

    Вводные параметры:
    - soup: экземпляр класса BeautifulSoup,
            необходимый для парсинга веб-сайта.
    - my_word: слово, которое необходимо перевести.

    Выводной параметр:
    - {my_word: dict_pos}: словарь, состоящий из английского слова
                           my_word и информационного словаря dict_pos.
               - dict_pos: словарь, содержащий информацию о переведенном слове
                           в разрезе отдельных частей речи (перевод, транскрипция,
                           примеры на английском и русском языках).
    """

    dict_pos = {}
    for item in soup.findAll(name="div", attrs={"class": "cforms_result"}):
        for item2 in item.findAll(name="div", attrs={'translation-item'}):

            pos = item. \
                find(
                    name="span", attrs={"class": "ref_psp"}
                ).text

            word = item2. \
                find(
                    name='span', attrs={'class': 'result_only sayWord'}
                ).text

            try:
                example_en = item2. \
                    find(
                        name='div', attrs={'class': 'samSource'}
                    ).text

                example_ru = item2. \
                    find(
                        name='div', attrs={'class': 'samTranslation'}
                    ).text

            except AttributeError:
                example_en, example_ru = None, None

            try:
                trans = item. \
                    find(
                        name='span', attrs={'class': 'transcription'}
                    ).text

            except AttributeError:
                trans = None

            if pos not in dict_pos:
                dict_pos[pos] = [{
                    'word': word,
                    'transcription': trans,
                    'example_en': example_en,
                    'example_ru': example_ru
                }]

            else:
                dict_pos[pos].append({
                    'word': word,
                    'transcription': trans,
                    'example_en': example_en,
                    'example_ru': example_ru
                })

    return {my_word: dict_pos}


def get_translation(my_word: str, os: str,
                    browser: str, attempts: int = 3,
                    error_timeout: int = 30) -> Optional[dict]:
    """
    Выводит перевод английских слов из онлайн-словаря PROMT.One.

    Вводные параметры:
    - my_word: слово, которое необходимо перевести.
    - os: название операционной системы в
          разрезе библиотеки fake_headers.
    - browser: название браузера в разрезе
               библиотеки fake_headers.
    - attempts: количество попыток парсинга сайта в
            условиях наличия возможной ошибки
            (requests.exceptions).
    - error_timeout: количество секунд остановки функции,
                     после которых последует реализация
                     следующей попытки осуществления
                     GET-запроса.

    Выводной параметр:
    - dict_info = {my_word: dict_pos}: словарь, полученный в рамках
                                       функции promt_site_parsing.
                                       (в случае удачного GET-запроса).
    """

    base_url = 'https://www.online-translator.com/'
    promt_link = base_url + 'translation/english-russian/'

    soup = launch_get_requests(
        attempts=attempts,
        error_timeout=error_timeout,
        promt_link=promt_link,
        my_word=my_word,
        os=os,
        browser=browser
        )

    if not soup:
        return None
    else:
        dict_info = promt_site_parsing(soup, my_word)
        return dict_info


def write_promt_translation(word_list: list, pos_list: str,
                            os: str, browser: str) -> list:
    """
    Записывает переведенные английские слова в отдельный csv-файл.

    Вводные параметры:
    - word_list: список английских слов, требующих перевода.
    - pos_list: список частей речи, учитываемых
                в разрезе онлайн-словаря PROMT.One.
    - os: название операционной системы в
          разрезе библиотеки fake_headers.
    - browser: название браузера в разрезе
               библиотеки fake_headers.

    Выводной параметр:
    word_trans_data: список, содержащий перевод слова и
                     прочую информацию о нем (транскрипция,
                     примеры предложений).
    """

    word_trans_data = []
    for my_word, pos in zip(word_list, pos_list):
        print(f'Обрабатываю слово {my_word}')

        try:
            trans = get_translation(
                my_word=my_word,
                os=os,
                browser=browser
            )[my_word][pos][0]
        except KeyError:
            trans = None

        if trans:
            word_trans_data.append([
                trans['word'],
                my_word,
                trans['transcription'],
                trans['example_en'],
                trans['example_ru']
            ])

    csv_path = write_dir(
        'data',
        'dictionary_data_csv',
        'promt_translation.csv'
    )

    if word_trans_data:
        with open(csv_path, 'w') as f:
            writer = csv.writer(f)
            writer.writerow([
                'ru_word',
                'en_word',
                'transcription',
                'example_en',
                'example_ru'
            ])
            writer.writerows(word_trans_data)

        print('Статус: слова успешно переведены (переводчик Promt)')
        return word_trans_data
