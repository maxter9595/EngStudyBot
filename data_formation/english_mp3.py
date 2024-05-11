import time
import requests

from data_formation.english_html import write_dir
from data_formation.english_html import get_headers


def write_mp3(url: str, file_path: str, os: str, browser: str,
              attempts: int, error_timeout: int) -> bool:
    """
    Проводит запись MP3 файла по URL-ссылке, полученной
    в результате реализации функции get_oxford_data.

    Вводные параметры:
    - url: URL-ссылка на MP3-файл, полученная
           из веб-сайта Оксфордского университета.
    - file_path: директория, относительно которой
                 необходимо записать MP3 файл на ПК.
    - os: название операционной системы в разрезе
          библиотеки fake_headers.
    - browser: название браузера в разрезе
               библиотеки fake_headers.
    - attempts: количество попыток парсинга сайта в
                условиях наличия возможной ошибки
                requests.exceptions.ConnectTimeout.
    - error_timeout: количество секунд остановки функции,
                     после которых последует реализация
                     следующей попытки осуществления
                     GET-запроса.

    Выводной параметр:
    - True/False: булевы значения, отражающие успешную/
                  безуспешную запись MP3 файла на ПК (папка data).
          - True: успешная запись файла.
         - False: неудачная запись файла.
    """

    attempt_count = 0
    for _ in list(range(1, attempts + 1)):
        if attempts >= attempt_count:
            try:
                headers = get_headers(
                    os_=os,
                    browser=browser
                )

                resp = requests.get(
                    url=url,
                    headers=headers,
                    timeout=10
                )

                resp.raise_for_status()

                with open(file_path, "wb") as fout:
                    fout.write(resp.content)

                return True

            except (requests.exceptions.ConnectTimeout,
                    requests.exceptions.ReadTimeout,
                    requests.exceptions.ConnectionError):
                print(f'requests.exceptions: не удалось обработать ссылку {url}')
                time.sleep(error_timeout)

        else:
            return False


def get_mp3_files(word_list: list, url_list: list,
                  transcript_list: list, os: str,
                  browser: str, attempts: int = 3,
                  error_timeout: int = 30) -> None:
    """
    Позволяет на основе списка слов и
    URL-ссылок массово записать MP3 файлы на ПК.

    Вводные параметры:
    - word_list: список английских слов.
    - url_list: список URL-ссылок на MP3-файлы.
    - transcript_list: список транскрипций английских слов.
    - os: название операционной системы
          в разрезе библиотеки fake_headers.
    - browser: название браузера в разрезе
               библиотеки fake_headers.
    - attempts: количество попыток парсинга сайта в
                условиях наличия возможной ошибки
                (requests.exceptions).
    - error_timeout: количество секунд остановки функции,
                     после которых последует реализация
                     следующей попытки осуществления
                     GET-запроса.
    """

    mp3_dict = {}
    for word, url, transcription in zip(word_list, url_list, transcript_list):
        print(f'Обрабатываю слово {word}')

        if transcription:
            mp3_name = f'{word} {transcription}.mp3'
            mp3_path = write_dir(
                'data',
                'eng_audio_files_mp3',
                mp3_name
            )

        else:
            mp3_name = f'{word[::-1].replace(" ", "", 1)[::-1]}.mp3'
            mp3_path = write_dir(
                'data',
                'eng_audio_files_mp3',
                mp3_name
            )

        mp3_bool = write_mp3(
            url=url,
            file_path=mp3_path,
            os=os,
            browser=browser,
            attempts=attempts,
            error_timeout=error_timeout
        )

        if mp3_bool and word not in mp3_dict:
            mp3_dict[word] = mp3_path
