import random

from telebot.storage import StateMemoryStorage
from telebot import types, TeleBot, custom_filters

from database.repository import DBRepository
from tgbot.parsing import Parsing
from tgbot.functionality import Functionality, Command, States


parsing = Parsing()
functionality = Functionality()
POS_LIST = ['noun', 'verb', 'adjective']


def start_game_handler(bot: TeleBot, repository: DBRepository) -> None:

    """
    Позволяет начать работу с чат-ботом и перейти к
    следующему выбору одного из четырех вариантов ответа.

    - bot: объект класса TeleBot, позволяющий выполнять
           функционал чат-бота Telegram (написание сообщения и др.).
    - repository: экземпляр класса DBRepository. Необходим для
                  подключения к БД пользователя чат-бота Telegram.
    """

    @bot.message_handler(commands=['cards', 'start'])
    def create_cards(message):
        chat_id = message.chat.id
        user_id = message.from_user.id

        user_data = repository.get_users(
            user_id=user_id
        )

        if not user_data:
            bot.send_message(
                user_id,
                functionality.hello_text()
            )

            user_dict = {
                'user_id': user_id,
                'first_name': message.from_user.first_name,
                'last_name': message.from_user.last_name,
                'username': message.from_user.username
            }

            repository.add_user(
                user_dict=user_dict
            )

            repository.prepare_user_word_pairs(
                user_id=user_id
            )

        user_database = repository.get_user_words(
            user_id=user_id,
            pos_name=random.choice(POS_LIST)
        )

        (target_word, translate, others, transcription,
         en_example, ru_example) = functionality.get_random_words(
            pos_database=user_database
        )

        global buttons
        buttons, markup = functionality.setup_buttons(
            target_word=target_word,
            others=others
        )

        bot.send_message(
            chat_id=chat_id,
            text=f"Выбери перевод слова:\n🇷🇺 {translate}",
            reply_markup=markup
        )

        bot.set_state(
            user_id=user_id,
            state=States.target_word,
            chat_id=chat_id
        )

        with bot.retrieve_data(user_id, chat_id) as data:
            data['target_word'] = target_word
            data['translate_word'] = translate
            data['other_words'] = others
            data['transcription'] = transcription
            data['en_example'] = en_example
            data['ru_example'] = ru_example

    @bot.message_handler(func=lambda message: message.text == Command.NEXT)
    def next_cards(message):
        create_cards(message)


def delete_word_handler(bot: TeleBot, repository: DBRepository) -> None:

    """
    Позволяет удалить имеющееся английское слово, введенное пользователем.

    - bot: объект класса TeleBot, позволяющий выполнять
           функционал чат-бота Telegram (написание сообщения и др.).
    - repository: экземпляр класса DBRepository. Необходим для
                  подключения к БД пользователя чат-бота Telegram.
    """

    @bot.message_handler(func=lambda message: message.text == Command.DELETE_WORD)
    def delete_word(message):
        chat_id = message.chat.id

        send_msg = bot.send_message(
            chat_id=chat_id,
            text="Введите английское слово для удаления из базы данных:"
        )

        bot.register_next_step_handler(
            message=send_msg,
            callback=delete_word_callback
        )

    def delete_word_callback(message):
        cid = message.chat.id
        user_id = message.from_user.id
        user_en_word = message.text.lower()
        user_database = repository.get_user_words(user_id=user_id)

        if user_en_word not in functionality.get_cmd_names():
            check_letters_bool = functionality.check_word_letters(
                word=user_en_word,
                eng_bool=True
            )

            if not check_letters_bool:
                bot.send_message(
                    chat_id=cid,
                    text=functionality.show_hint(*[
                        'Слово должно содержать только английские буквы.',
                        '',
                        'Пожалуйста, повторите попытку нажатием на кнопку',
                        f'{Command.DELETE_WORD.lower()}'])
                )

            else:
                repository.remove_user_word(
                    user_id=user_id,
                    en_word=user_en_word
                )

                new_user_database = repository.get_user_words(
                    user_id=user_id
                )

                if len(new_user_database) == len(user_database):
                    bot.send_message(
                        chat_id=cid,
                        text='Введенное слово отсутсвует в базе данных пользователя'
                    )

                else:
                    bot.send_message(
                        chat_id=cid,
                        text=f'Слово "{user_en_word}" удалено'
                    )

                    unique_words = repository.get_unique_user_words(
                        user_id=user_id
                    )

                    bot.send_message(
                        chat_id=cid,
                        text=f'Текущее количество английских слов - {len(unique_words)} шт.'
                    )

        else:
            bot.send_message(
                chat_id=cid,
                text=functionality.show_hint(*[
                    'Я принимаю только слова.',
                    f'Команда {user_en_word} в расчет не берется.'])
            )


def add_word_handler(bot: TeleBot, repository: DBRepository) -> None:

    """
    Позволяет добавить новое английское слово, введенное пользователем.

    - bot: объект класса TeleBot, позволяющий выполнять
           функционал чат-бота Telegram (написание сообщения и др.).
    - repository: экземпляр класса DBRepository. Необходим для
                  подключения к БД пользователя чат-бота Telegram.
    """

    @bot.message_handler(func=lambda message: message.text == Command.ADD_WORD)
    def add_word(message):
        cid = message.chat.id

        send_msg = bot.send_message(
            chat_id=cid,
            text="Введите английское слово для добавления в базу данных:"
        )

        bot.register_next_step_handler(
            message=send_msg,
            callback=add_en_word_callback
        )

    def add_en_word_callback(message):
        cid = message.chat.id
        user_id = message.from_user.id
        user_en_word = message.text.lower()

        if user_en_word not in functionality.get_cmd_names():
            if '❌' not in user_en_word:
                check_letters_bool = functionality.check_word_letters(
                    word=user_en_word,
                    eng_bool=True
                )

                if check_letters_bool:
                    user_database = repository.get_user_words(
                        user_id=user_id
                    )

                    existing_words = repository.get_unique_user_words(
                        user_id=user_id
                    )

                    if user_en_word in existing_words:
                        bot.send_message(
                            chat_id=cid,
                            text='Английское слово уже существует'
                        )

                    else:
                        new_word_info = parsing.get_word_info(
                            en_word=user_en_word,
                            pos_list=POS_LIST,
                            os_='win',
                            browser='chrome'
                        )

                        if new_word_info[0].get('ru_word') is None:
                            data_dict = new_word_info.pop()
                            data_dict['ru_word'] = ''

                            repository.add_user_word(
                                user_id=user_id,
                                data_dict=data_dict
                            )

                            send_msg = bot.send_message(
                                chat_id=cid,
                                text="Введите перевод английского слова:"
                            )

                            bot.register_next_step_handler(
                                message=send_msg,
                                callback=add_ru_word_callback
                            )

                        else:
                            for word_dict in new_word_info:
                                repository.add_user_word(
                                    user_id=user_id,
                                    data_dict=word_dict
                                )

                            new_user_database = repository.get_user_words(
                                user_id=user_id
                            )

                            if len(user_database) != len(new_user_database):
                                unique_words = repository.get_unique_user_words(
                                    user_id=user_id
                                )

                                bot.send_message(
                                    chat_id=cid,
                                    text=f'Текущее количество английских слов - {len(unique_words)} шт.'
                                )

                else:
                    bot.send_message(
                        chat_id=cid,
                        text=functionality.show_hint(*[
                            'Слово должно содержать только английские буквы.',
                            '',
                            'Пожалуйста, повторите попытку нажатием на кнопку',
                            f'{Command.ADD_WORD.lower()}'])
                    )

            else:
                bot.send_message(
                    chat_id=cid,
                    text='Английское слово уже существует в пользовательской БД'
                )

        else:
            bot.send_message(
                chat_id=cid,
                text=functionality.show_hint(*[
                    'Я принимаю только слова.',
                    f'Команда {user_en_word} в расчет не берется.'])
            )

    def add_ru_word_callback(message):
        cid = message.chat.id
        user_id = message.from_user.id
        user_ru_word = message.text.lower()

        user_database = repository.get_user_words(
            user_id=user_id
        )

        last_en_word = user_database[-1].get('en_word')

        data_dict = {
            'en_word': last_en_word,
            'en_trans': '',
            'mp_3_url': '',
            'pos_name': 'unidentified',
            'ru_word': user_ru_word,
            'en_example': '',
            'ru_example': ''
        }

        check_letters_bool = functionality.check_word_letters(
            word=user_ru_word,
            eng_bool=False
        )

        if check_letters_bool:
            repository.add_user_word(
                user_id=user_id,
                data_dict=data_dict
            )

            unique_words = repository.get_unique_user_words(
                user_id=user_id
            )

            bot.send_message(
                chat_id=cid,
                text=f'Текущее количество английских слов - {len(unique_words)} шт.'
            )

        else:
            repository.delete_user_word_pair(
                user_id=message.from_user.id,
                en_word=last_en_word
            )

            repository.delete_word(
                data_dict=data_dict
            )

            bot.send_message(
                chat_id=cid,
                text=functionality.show_hint(*[
                    'В этом случае я принимаю только русские буквы.',
                    '',
                    'Пожалуйста, повторите попытку нажатием на кнопку',
                    f'{Command.ADD_WORD.lower()}'])
            )


def reply_handler(bot: TeleBot) -> None:

    """
    Формирует отклик на выбор английского слова пользователем чат-бота Telegram.

    - bot: объект класса TeleBot, позволяющий выполнять
           функционал чат-бота Telegram (написание сообщения и др.).
    """

    @bot.message_handler(func=lambda message: True, content_types=['text'])
    def message_reply(message):
        text = message.text
        cid = message.chat.id
        user_id = message.from_user.id
        markup = types.ReplyKeyboardMarkup(row_width=2)

        try:
            with bot.retrieve_data(user_id, cid) as data:
                target_word = data['target_word']

                if text == target_word:
                    hint = functionality.show_target(data)
                    hint = functionality.show_hint(*["Отлично!❤", hint])

                else:
                    for btn in buttons[:4]:
                        if btn.text == text:
                            if '❌' not in btn.text:
                                btn.text = text + '❌'

                            hint = functionality.show_hint(*[
                                "Допущена ошибка!",
                                f"Попробуй ещё раз вспомнить слово 🇷🇺{data['translate_word']}"
                            ])
                            break

            markup.add(*buttons)

            msg = bot.send_message(
                chat_id=cid,
                text=hint,
                reply_markup=markup
            )

            functionality.get_mp3_audio(
                bot=bot,
                data=data,
                hint=hint,
                message=msg
            )

            functionality.get_example(
                bot=bot,
                message=message,
                markup=markup,
                data=data,
                hint=hint
            )

        except (TypeError, KeyError, UnboundLocalError):
            pass


def connect_telebot(repository: DBRepository, token: str) -> None:

    """
    Позволяет подключиться к телеграм-боту.

    - repository: экземпляр класса DBRepository. Необходим для
                  подключения к БД пользователя чат-бота Telegram.
    - token_bot: токен для подключения к чат-боту Telegram.
    """

    bot = TeleBot(
        token=token,
        state_storage=StateMemoryStorage()
    )

    start_game_handler(
        bot=bot,
        repository=repository
    )

    delete_word_handler(
        bot=bot,
        repository=repository
    )

    add_word_handler(
        bot=bot,
        repository=repository
    )

    reply_handler(
        bot=bot
    )

    bot.add_custom_filter(
        custom_filter=custom_filters.StateFilter(bot)
    )

    bot.infinity_polling(
        skip_pending=True
    )
