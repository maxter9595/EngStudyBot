import re
import os
import csv

import requests
from bs4 import BeautifulSoup
from fake_headers import Headers


def get_oxford_data(soup: BeautifulSoup, base_url: str) -> list:
    """
    Позволяет загрузить английские слова, входящие в сборник Oxford 5000.

    Вводные параметры:
    - soup: объект класса BeautifulSoup,
            необходимый для парсинга веб-сайта.
    - base_url: URL-адрес страницы. В данном случае
                это ссылка на онлайн-словарь
                Оксфордского университета.

    Выводной параметр:
    - word_list: список, содержащий информацию о
                 загруженных словах, включенных в сборник
                 Oxford 5000 (слово, часть речи, уровень
                 владения английским языком, ссылка на MP3
                 файл произношения слова).
    """

    word_list = []
    for item in soup.findAll(name="ul", attrs={"class": "top-g"}):
        for item2 in item.findAll(name="li"):
            try:
                word = item2. \
                    find(name='a'
                         ).text

                pos = item2. \
                    find(name='span', attrs={'class': 'pos'}
                         ).text

                lvl = item2. \
                    find(name='span', attrs={'class': 'belong-to'}
                         ).text

                mp3_find = item2. \
                    find(name='div', attrs={
                        'class': 'sound audio_play_button icon-audio pron-uk'}
                         )

                mp3_search = re.search(r"mp3=(.+mp3.)", str(mp3_find)). \
                    group(1).replace('"', '')

                mp3_link = base_url[:-1] + mp3_search

                if word:
                    print(f'Обрабатываю слово {word}')
                    word_list.append([
                        word,
                        pos,
                        lvl,
                        mp3_link
                    ])

            except AttributeError:
                pass

    return word_list


def write_dir(*args) -> os.path:
    """
    Выводит путь к файлу, состоящий
    из заданных аргументов.

    Вводный параметр:
    - *args: аргументы, используемые
             для формирования директории.

    Выводной параметр:
    - root_dir: путь к файлу.
    """

    abspath = os.path.abspath(path=args[0])

    root_dir = ''
    for arg in args[1:]:
        if root_dir:
            root_dir = os.path.join(root_dir, arg)
        else:
            root_dir = os.path.join(abspath, arg)
    return root_dir


def get_headers(os_: str, browser: str) -> dict:
    """
    Создает фейковые заголовки, необходимые
    для работы с функционалом библиотеки requests.

    Вводные параметры:
    os:_ название операционной системы
         в разрезе библиотеки fake_headers.
    browser: название браузера в разрезе
             библиотеки fake_headers.

    Выводной параметр:
    - Словарь-заголовок, необходимый для
      работы с функциями библиотеки requests.
    """

    return Headers(
        os=os_,
        browser=browser
    ).generate()


def write_oxford_data(os_: str, browser: str) -> list:
    """
    Записывает данные английских слов
    на локальный файл проекта.

    Вводные параметры:
    - os: название операционной системы в
          разрезе библиотеки fake_headers.
    - browser: название браузера в разрезе
               библиотеки fake_headers.

    Выводной параметр:
    - data: лист с данными, полученными в
            результате отработки функции
            get_oxford_data.
    """

    base_url = 'https://www.oxfordlearnersdictionaries.com/'
    oxford5000_url = base_url + 'wordlists/oxford3000-5000'

    headers = get_headers(
        os_=os_,
        browser=browser
    )

    resp = requests.get(
        url=oxford5000_url,
        headers=headers
    )

    soup = BeautifulSoup(
        markup=resp.content,
        features="lxml"
    )

    data = get_oxford_data(
        soup=soup,
        base_url=base_url
    )

    col_names = [
        'word',
        'pos',
        'level',
        'mp3_url'
    ]

    csv_path = write_dir(
        'data',
        'dictionary_data_csv',
        'oxford5000_dictionary.csv'
    )

    with open(csv_path, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(col_names)
        writer.writerows(data)

    print('Статус: английские слова словаря Oxford 5000 получены')
    return data
