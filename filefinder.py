import os
from typing import Optional


def find_file(file_name: str) -> Optional[str]:

    """
    Позволяет найти путь к файлу относительно проекта.

    Вводный параметр:
    - file_name: название файла, который хотим найти относительно проекта

    Выводной параметр:
    - путь к заданному файлу (в случае его наличия)
    """

    search_path = os.path.dirname(os.path.abspath(__file__))

    for dirpath, dirnames, filenames in os.walk(search_path):
        if file_name in filenames:
            return os.path.join(dirpath, file_name)


def find_folder(folder_name: str) -> Optional[str]:

    """
    Позволяет найти путь к папке относительно проекта.

    Вводный параметр:
    - folder_name: название папки, которую хотим найти относительно проекта

    Выводной параметр:
    - путь к заданной папке (в случае его наличия)
    """

    search_path = os.path.dirname(os.path.abspath(__file__))

    for dirpath, dirnames, filenames in os.walk(search_path):
        if folder_name in dirnames:
            return os.path.join(dirpath, folder_name)