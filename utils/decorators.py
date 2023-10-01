import time
from functools import wraps
from pprint import pprint

from termcolor import cprint

from utils.config import bot, chat_id, topic_id


def timer(func):
    """Декоратор времени выполнения функции"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        t_start = time.perf_counter()
        value = func(*args, **kwargs)

        if value:
            t_stop = time.perf_counter()
            t_process = round(((t_stop - t_start) / 60), 2)
            cprint(f"Время выполнения: {t_process}", "light_green")

        return value

    return wrapper


def notification_bot(bool_value: bool = False):
    """Уведомление через бота"""

    def inner(func):
        @wraps(func)
        def wrapper(*args_, **kwargs_):
            result_func = func(*args_, **kwargs_)

            if result_func:
                text, errors = result_func

                if errors != []:
                    pprint(errors, sort_dicts=False)
                    bot.send_message(
                        chat_id=chat_id, text=str(errors), reply_to_message_id=topic_id
                    )

                print(text)

                if bool_value:
                    bot.send_message(
                        chat_id=chat_id, text=text, reply_to_message_id=topic_id
                    )

        return wrapper

    return inner


def mult_threading(func):
    """Декоратор для запуска функции в отдельном потоке"""

    @wraps(func)
    def wrapper(*args_, **kwargs_):
        import threading

        func_thread = threading.Thread(target=func, args=tuple(args_), kwargs=kwargs_)
        func_thread.start()
        return func_thread

    return wrapper


def exception_handler(func):
    """Декоратор ошибок"""

    @wraps(func)
    def wrapper(*args_, **kwargs_):
        while True:
            try:
                return func(*args_, *kwargs_)
            except KeyError:
                cprint("Ошибка параметров команды!", "light_red")

    return wrapper
