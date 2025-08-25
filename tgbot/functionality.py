import os
import re
import random
from typing import Optional
from string import ascii_letters

import telebot
from telebot import TeleBot, types
from telebot.asyncio_handler_backends import StatesGroup, State

from filefinder import find_folder


class Command:
    ADD_WORD = 'Добавить слово ➕'
    DELETE_WORD = 'Удалить слово🔙'
    NEXT = 'Дальше ⏭'


class States(StatesGroup):
    target_word = State()
    translate_word = State()
    another_words = State()


class Functionality:

    def setup_buttons(self, target_word: str, others: list) -> tuple:

        """
        Настраивает клавишный функционал чат-бота Telegram.

        Вводные параметры:
        - target_word: целевое слово
        - others: список с остальными рандомными словами

        Выводные параметры:
        - (buttons, markup): кортеж с переменными, затрагивающими клавишный функционал.
            -- buttons: список объектов класса KeyboardButton, отражающих принадлежность
                        клавиш к тому или иному выборочному английскому слову.
            -- markup: объект класса ReplyKeyboardMarkup, отвечающий за формирование
                       разметки клавиатуры и отклик на ее нажатие.
        """

        target_word_btn = [types.KeyboardButton(target_word)]

        other_words_btns = []
        for word in others:
            other_words_btns.append(
                types.KeyboardButton(word)
            )

        buttons = target_word_btn + other_words_btns
        random.shuffle(buttons)

        buttons.extend([
            types.KeyboardButton(Command.NEXT),
            types.KeyboardButton(Command.ADD_WORD),
            types.KeyboardButton(Command.DELETE_WORD)
        ])

        markup = types.ReplyKeyboardMarkup(row_width=2)
        markup.add(*buttons)

        return buttons, markup

    def get_cmd_names(self) -> tuple:

        """
        Выводит кортеж с названиями кнопочных команд,
        указанных в классе Command.

        Выводные параметры:
        - кортеж с названиями кнопочных команд:
            -- add_btn_name: название клавиши, отвечающей за добавление слова.
            -- delete_btn_name: название клавиши, отвечающей за удаление слова.
            -- next_btn_name: название клавиши, отвечающей за продолжение выбора слов.
        """

        add_btn_name = Command.ADD_WORD.lower()
        delete_btn_name = Command.DELETE_WORD.lower()
        next_btn_name = Command.NEXT.lower()

        return add_btn_name, delete_btn_name, next_btn_name

    def get_example(self, bot: TeleBot, message: telebot.types.Message,
                    markup: telebot.types.ReplyKeyboardMarkup,
                    data: dict, hint: str) -> None:

        """
        Выводит пример предложения с использованием
        выбранного английского слова в чате Telegram.

        Вводные параметры:
        - bot: объект класса TeleBot, позволяющий выполнять функционал
              чат-бота Telegram (написание сообщения и др.).
        - message: объект класса Message, позволяющий определить
                  ID чата пользователя Telegram.
        - markup: объект класса ReplyKeyboardMarkup, отвечающий за формирование
                 разметки клавиатуры и отклик на ее нажатие.
        - data: словарь с данными, фиксируемыми в памяти бота.
        - hint: строка, отражающая ответ чат-бота на выбор одного
               из четырех вариантов слов.
        """

        if 'Допущена ошибка!' not in hint:
            if data['en_example'] != 'No example' and \
                    data['ru_example'] != "Пример отсутствует":
                en_example = data["en_example"]
                ru_example = data["ru_example"]

                example_text = self.show_hint(
                    '*Пример предложения:*',
                    f'"{en_example}"',
                    f'"{ru_example}"'
                )

                bot.send_message(
                    chat_id=message.chat.id,
                    text=example_text,
                    reply_markup=markup,
                    parse_mode='Markdown'
                )

    def get_mp3_audio(self, bot: TeleBot, data: dict, hint: str,
                    message: telebot.types.Message) -> None:

        """
        Запускает MP3-файл в чате Telegram.
        """

        if 'Допущена ошибка!' not in hint:
            word = data['target_word']
            transcription = data['transcription']

            safe_word = re.sub(r'[<>:"/\\|?*]', '', word)
            safe_transcription = re.sub(r'[<>:"/\\|?*]', '', transcription) if transcription else ""

            if safe_transcription:
                mp3_name = f"{safe_word} {safe_transcription}.mp3"
            else:
                mp3_name = f"{safe_word}.mp3"

            mp3_path = os.path.join(
                find_folder('eng_audio_files_mp3'),
                mp3_name
            )

            if not os.path.exists(mp3_path):
                from tgbot.parsing import Parsing
                parsing = Parsing()
                
                oxford_data = parsing.receive_oxford_data(
                    en_word=word,
                    os_='win',
                    browser='chrome'
                )
                
                if oxford_data.get('mp_3_url'):
                    parsing.write_user_mp3(
                        en_word=word,
                        mp_3_url=oxford_data.get('mp_3_url'),
                        transcription=transcription,
                        os_='win',
                        browser='chrome'
                    )

            try:
                if os.path.exists(mp3_path):
                    bot.send_audio(
                        chat_id=message.chat.id,
                        audio=open(mp3_path, 'rb'),
                        title=f"{word}",
                        performer="Oxford Dictionary"
                    )
                    print(f'MP3 файл отправлен: {mp3_path}')
                else:
                    print(f'Аудиофайл не найден: {mp3_path}')
            except Exception as e:
                print(f'Ошибка при отправке аудиофайла: {e}')

    def check_word_letters(self, word: str, eng_bool: bool = True) -> bool:

        """
        Проверяет наличие английских/русских букв в слове, указанном
        пользователем во время реализации команд "Добавить слово"
        и "Удалить слово".

        Вводные параметры:
        - word: слово, требуещее проверки на
                наличие английских/русских букв.
        - eng_bool: переменная булева типа, отвечающая за
                    выбор английского или русского алфавита.
            -- True: выбираются только буквы английского алфавита.
            -- False: выбираются только буквы русского алфавита.

        Выводной параметр:
        - переменная булева типа, отражающая соответствие (True)
          или несоответствие (False) слова на наличие исключительно
          английских/русских букв.
        """

        if eng_bool:
            letter_condition = lambda letter:\
                letter in ascii_letters
        else:
            letter_condition = lambda letter:\
                re.match('[а-яА-ЯёЁ]', letter)

        for letter in word:
            if letter.isalpha() and\
                    letter_condition(letter):
                continue
            else:
                return False
        return True

    def get_random_words(self, pos_database: list) -> Optional[tuple]:

        """
        Выбирает целевое английское слово.

        Вводный параметр:
        - pos_database: список с данными английских слов,
                        принадлежащих к БД пользователя
                        Telegram и конкретной части речи.

        Выводные параметры:
        - tuple: кортеж с данными.
            -- target_word: целевое английское слово, которое необходимо
                            угадать пользователю чат-бота Telegram.
            -- translate: перевод целевого английского слова target_word.
            -- other_words: список остальных трех английских слов, являющихся
                            некорректными вариантами ответа. Выбираются
                            рандомным образом.
            -- transcription: транскрипция целевого английского слова target_word.
            -- en_example: пример английского предложения с использованием
                           целевого слова target_word.
            -- ru_example: пример русского предложения с использованием
                           перевода translate.
        """

        total_words = len(pos_database)

        if total_words >= 4:
            target_idx = random.randint(0, total_words - 1)  # Исправлено: индексы от 0 до total_words-1
            target_dict = pos_database[target_idx]
            target_word = target_dict.get('en_word')

            other_words = []
            while len(other_words) < 3:
                other_idx = random.randint(0, total_words - 1)  # Исправлено: индексы от 0 до total_words-1

                if other_idx != target_idx:
                    other_word = pos_database[other_idx].get('en_word')

                    if other_word != target_word and other_word not in other_words:
                        other_words.append(other_word)

            ru_translation = target_dict.get('ru_word')
            transcription = target_dict.get('en_trans', '')
            en_example = target_dict.get('en_example', 'No example')
            ru_example = target_dict.get('ru_example', 'Пример отсутствует')

            return (target_word, ru_translation, other_words,
                    transcription, en_example, ru_example)

    def show_hint(self, *lines: str) -> str:

        """
        Выводит подсказку в чат Telegram бота при наличии
        корректного/некорректного действия со стороны пользователя
        чат-бота Telegram (выбор корректного/некорректного ответа,
        ввод некорректного слова для его добавления в БД/удаления из БД).

        Вводный параметр:
        - lines: список, состоящий из строковых аргументов. Вместе они
                 образовывают ответное сообщение чат-бота Telegram.
        """

        return '\n'.join(lines)

    def hello_text(self) -> str:

        """
        Пишет новому пользователю чат-бота Telegram
        приветственный текст, описывающий принципы работы
        чат-бота Telegram.
        """

        text = """
        Привет 👋 Давай попрактикуемся в английском языке.

        Тренировки можешь проходить в удобном для себя темпе.

        Для этого воспользуйся следующимим инструментами:
        дальше ⏭
        добавить слово ➕,
        удалить слово 🔙.

        Ну что, начнём ⬇️
        """

        return '\n'.join(
            line.lstrip() for line in text.splitlines()
        )

    def show_target(self, data: dict) -> str:
        """
        Выводит строку "целевое англ. слово [транскрипция] -> перевод слова" в чат
        Telegram бота при наличии корректного ответа пользователя.
        """
        
        target_word = data['target_word']
        transcription = data['transcription']
        translate_word = data['translate_word']
        
        if transcription and transcription.strip():
            return f"{target_word} {transcription} → {translate_word}"
        else:
            return f"{target_word} → {translate_word}"