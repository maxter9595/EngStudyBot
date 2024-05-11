import csv

from data_formation.english_html import write_oxford_data, write_dir
from data_formation.translation_html import write_promt_translation
from data_formation.english_mp3 import get_mp3_files


def get_pos_data(oxford_data_list: list,
                 oxford_pos_list: list) -> tuple:
    """
    Фильтрует английские слова по частям речи
    (существительные, глаголы, прилагательные).

    Вводные параметры:
    - oxford_data_list: список с данными английских
                        слов, полученных из функции
                        write_oxford_data.
    - oxford_pos_list: список частей речи, по которым
                       фильтруются слова.

    Выводной параметр:
    - (pos_data_list, pos_word_list, pos_list): кортеж с данными,
                                                полученными после
                                                фильтрации слов.
        -- pos_data_list: список с информацией
                          относительно английских
                          слов (слово, часть речи,
                          уровень владения английским
                          языком, ссылка на MP3 файл
                          произношения слова).
        -- pos_word_list: список английских слов.
        -- pos_list: список частей речи.
    """

    pos_data_list, pos_word_list, pos_list = [], [], []

    verb_tuple = (
        'verb', 'linking verb',
        'modal verb', 'auxiliary verb'
    )

    for loop_list in oxford_data_list:
        if loop_list[1] in oxford_pos_list:
            if loop_list[1] in verb_tuple:
                loop_list[1] = 'verb'

            if loop_list not in pos_data_list:
                pos_data_list.append(loop_list)
                pos_word_list.append(loop_list[0])
                pos_list.append(loop_list[1])

    return pos_data_list, pos_word_list, pos_list


def get_processed_data(word_trans_data: list,
                       pos_data_list: list,
                       pos_word_list: list) -> list:
    """
    Объединяет данные английских слов из
    онлайн-словаря Oxford и сведения, полученные
    из онлайн-словаря PROMT.One.

    Вводные параметры:
    - word_trans_data: список, содержащий перевод слова и
                       прочую информацию о нем (транскрипция,
                       примеры предложений).
    - pos_data_list: список с информацией относительно английских
                     слов (слово, часть речи, уровень владения
                     английским языком, ссылка на MP3 файл
                     произношения слова).
    - pos_word_list: список английских слов.

    Выводной параметр:
    - processed_data_list: список с обработанными данными (английское
                           слово, часть речи, уровень владения английским
                           языком, ссылка на MP3-файл, перевод слова,
                           транскрипция, примеры использования слова на
                           английском и русском языках).
    """

    processed_data_list = []
    for word in pos_word_list:
        data_list1 = [
            my_list for my_list in pos_data_list
            if my_list[0] == word
        ]

        data_list2 = [
            my_list for my_list in word_trans_data
            if my_list[1] == word and my_list[-1] != '' and my_list[-2] != ''
        ]

        if data_list2:
            processed_data_list. \
                append(data_list1[0] + [data_list2[0][0]] + data_list2[0][2:]
                       )

    processed_data_list = [
        list(x) for x in set(tuple(x) for x in processed_data_list)
    ]

    return processed_data_list


def write_processed_data(processed_data_list: list) -> None:
    """
    Запись обработанных данных, выведенных
    из функции get_processed_data, на ПК.

    Вводный параметр:
    - processed_data_list: список с обработанными данными
                           (английское слово, часть речи,
                           уровень владения английским языком,
                           ссылка на MP3-файл, перевод слова,
                           транскрипция, примеры использования
                           слова на английском и русском языках).
    """

    csv_db_path = write_dir(
        'data',
        'database_csv',
        'database.csv'
    )

    col_names = [
        'en_word',
        'pos',
        'level',
        'mp3_url',
        'ru_word',
        'transcription',
        'en_example',
        'ru_example'
    ]

    with open(csv_db_path, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(col_names)
        writer.writerows(processed_data_list)


def download_mp3(processed_data_list: list,
                 os: str, browser: str) -> None:
    """
    Записывает MP3 файлы на основе URL-ссылок,
    содержащихся в списке с обработанными данными
    (processed_data_list).

    Вводные параметры:
    - processed_data_list: список с обработанными данными
                          (английское слово, часть речи,
                          уровень владения английским языком,
                          ссылка на MP3-файл, перевод слова,
                          транскрипция, примеры использования
                          слова на английском и русском языках).
    - os: название операционной системы в
          разрезе библиотеки fake_headers.
    - browser: название браузера в разрезе
               библиотеки fake_headers.
    """

    word_list, url_mp3_list, trascription_list = [], [], []

    for list_ in processed_data_list[1:]:
        en_word, url_mp3, trascription = (list_[0], list_[3], list_[5])
        word_list.append(en_word)
        url_mp3_list.append(url_mp3)
        trascription_list.append(trascription)

    get_mp3_files(
        word_list, url_mp3_list,
        trascription_list, os, browser
    )


def form_english_data(os: str = 'win', browser: str = 'chrome') -> None:
    """
    Формирует данные английских слов: файл database.csv
    и MP3-файлы с произношением английских слов.

    Вводные параметры:
    - os: название операционной системы в разрезе
          библиотеки fake_headers.
    - browser: название браузера в разрезе
               библиотеки fake_headers.
    """

    print('ПОЛУЧЕНИЕ АНГЛИЙСКИХ СЛОВ (OXFORD):')

    oxford_data_list = write_oxford_data(
        os_=os,
        browser=browser
    )

    oxford_pos_list = [
        'noun', 'verb', 'linking verb',
        'modal verb', 'auxiliary verb', 'adjective'
    ]

    (pos_data_list, pos_word_list, pos_list) = get_pos_data(
        oxford_data_list=oxford_data_list,
        oxford_pos_list=oxford_pos_list
    )

    print('ПЕРЕВОД СЛОВ И ПОДБОР ПРИМЕРОВ ПРЕДЛОЖЕНИЙ (PROMT):')

    word_trans_data = write_promt_translation(
        word_list=pos_word_list,
        pos_list=pos_list,
        os=os,
        browser=browser
    )

    print('ПОЛУЧЕНИЕ ОБРАБОТАННЫХ ДАННЫХ (OXFORD+PROMT):')

    processed_data_list = get_processed_data(
        word_trans_data=word_trans_data,
        pos_data_list=pos_data_list,
        pos_word_list=pos_word_list
    )

    write_processed_data(
        processed_data_list=processed_data_list
    )

    print('Статус: данные успешно записаны')
    print('ВЫВОД MP3 ФАЙЛОВ ПО URL-ССЫЛКАМ:')

    download_mp3(
        processed_data_list=processed_data_list,
        os=os,
        browser=browser
    )

    print('Статус: MP3 файлы успешно записаны')


if __name__ == '__main__':
    form_english_data()
