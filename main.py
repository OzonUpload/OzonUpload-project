import datetime
import os
import sys
from pathlib import Path
from traceback import print_exception

import OzonSeller_api
import str_mobile
from prompt_toolkit import PromptSession
from prompt_toolkit import print_formatted_text as print
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.history import FileHistory
from termcolor import cprint

from handlers.GroupsUpdate import GroupsUpdateMain
from handlers.ozon import OzonMain
from handlers.parser import ParserMain
from handlers.Update.update_prices import update_prices
from handlers.Update.update_stocks import update_stocks
from utils.config import Configurate, city, style
from utils.create_dir import PATH_HISTORY, PATH_PROJECT
from utils.decorators import mult_threading
from utils.get_data import get_data

config = Configurate().config

__version__ = "1.7.7"

sys.stdout.write("\033[H\033[J")


class Main:
    """Класс программы"""

    def __init__(self):
        self.ozon_main = OzonMain()
        self.parser_main = ParserMain()
        self.groups_update = GroupsUpdateMain()
        self.worked_update_stocks = False
        self.worked_update_prices = False
        sys.excepthook = self.exception_handler

        session = PromptSession(
            history=FileHistory(PATH_HISTORY / Path("history_main"))
        )
        commands_completer = NestedCompleter.from_nested_dict(
            {
                "ozon": None,
                "parser": {"str_mobile": None},
                "create": {"group": None},
                "get": {"groups": None},
                "update": {
                    "stocks": {
                        "full": None,
                        "category": None,
                        "product": {"id": None, "article": None, "code": None},
                    },
                    "prices": {
                        "full": None,
                        "category": None,
                        "product": {"id": None, "article": None, "code": None},
                    },
                },
                "start": {
                    "update": {
                        "stocks": {
                            "full": None,
                            "category": None,
                            "product": {"id": None, "article": None, "code": None},
                        },
                        "prices": {
                            "full": None,
                            "category": None,
                            "product": {"id": None, "article": None, "code": None},
                        },
                    },
                    "group": None,
                },
                "stop": {"update": {"stocks": None}},
                "open": {
                    "settings": {
                        "ozon": None,
                        "parser": {"str_mobile": None},
                        "OzonUpload": None,
                    }
                },
                "exit": None,
            }
        )
        message = [("class:project", "OzonUpload"), ("class:sign_more", ">")]

        while True:
            text: str = session.prompt(
                message=message, completer=commands_completer, style=style
            ).strip()

            if len(text.split(" ")) > 1:
                value = text.split()
            else:
                value = text

            match value:
                case "ozon":
                    self.ozon_main()
                case "parser", site:
                    self.parser_main.get_site_class(site=site)

                # create
                case "create", "group", group_name:
                    self.groups_update.create_group(group_name=group_name)
                # get
                case "get", "groups":
                    [
                        print(f"{i}. {group_name}")
                        for i, group_name in enumerate(
                            self.groups_update.get_groups_updates().keys(), start=1
                        )
                    ]
                # update
                case "update", "stocks", *args_command:
                    update_stocks(args_command=args_command)
                case "update", "prices", *args_command:
                    update_prices(args_command=args_command)
                # start
                case "start", "update", "stocks", *args_command:
                    self.start_update_stocks(args_command=args_command)
                case "start", "update", "prices", *args_command:
                    self.start_update_prices(args_command=args_command)
                case "start", "group", group_name:
                    self.groups_update.start_group_update(group_name=group_name)
                # stop
                case "stop", "update", "stocks":
                    self.worked_update_stocks = False
                    cprint("Остановлено!", "light_blue")
                case "stop", "update", "prices":
                    self.worked_update_prices = False
                    cprint("Остановлено!", "light_blue")
                # open
                case "open", "settings", "ozon":
                    os.system(f" start {OzonSeller_api.PATH_PROJECT}")
                    cprint("Папа открыта!", "light_blue")
                case "open", "settings", "OzonUpload":
                    os.system(f"start {PATH_PROJECT}")
                    cprint("Папа открыта!", "light_blue")
                case "open", "settings", "parser", site_name:
                    if site_name == "str_mobile":
                        os.system(f"start {str_mobile.PATH_MODULE_PROJECT}")
                        cprint("Папа открыта!", "light_blue")
                    else:
                        cprint(
                            "Такого сайта поставщиков нету в программе!", "light_blue"
                        )
                # exit
                case "exit":
                    self.worked_update_stocks = False
                    self.worked_update_prices = False
                    break
                case _:
                    cprint("Вы ввели нерпавильную команду!", "light_red")

    def exception_handler(
        self, exectype: type[BaseException], value: BaseException, traceback
    ):
        """Обработка неотловленных ошибок"""
        if exectype == KeyboardInterrupt:
            """Нажатие CTRL+C"""
            cprint("Выход!", "light_red")
            self.worked_update_stocks = False
            self.worked_update_prices = False
        elif exectype == EOFError:
            """Нажатие CTRL+D"""
            cprint("Выход!", "light_red")
            self.worked_update_stocks = False
            self.worked_update_prices = False
        else:
            print("=" * 100)
            print_exception(exectype, value, traceback)
            print("=" * 100)

    @mult_threading
    def start_update_stocks(self, args_command: list[str]):
        """Запуск автоматического обновления остатков"""

        filters_weekday = [datetime.time(hour) for hour in [11, 14, 19]]

        filters_weekends = [datetime.time(11)]

        if self.worked_update_stocks:
            cprint("Уже запущено", "light_red")
            return
        else:
            cprint("Запущено!", "light_blue")
            self.worked_update_stocks = True

        while self.worked_update_stocks:
            data_time = get_data(city=city)
            time = datetime.time(data_time.hour, data_time.minute, data_time.second)
            day_week = data_time.strftime("%w")
            if int(day_week) in range(1, 6):
                if time in filters_weekday:
                    cprint(f"Начало обновления в {time}!", "light_blue")
                    update_stocks(args_command=args_command)
            elif day_week == "6":
                if time in filters_weekends:
                    cprint(f"Начало обновления в {time}!", "light_blue")
                    update_stocks(args_command=args_command)

    @mult_threading
    def start_update_prices(self, args_command: list[str]):
        """Запуск автоматического обновления цен"""

        filters_weekday = [datetime.time(hour) for hour in [11, 14, 19]]

        filters_weekends = [datetime.time(11)]

        if self.worked_update_prices:
            cprint("Уже запущено", "light_red")
            return
        else:
            cprint("Запущено!", "light_blue")
            self.worked_update_prices = True

        while self.worked_update_prices:
            data_time = get_data(city=city)
            time = datetime.time(data_time.hour, data_time.minute, data_time.second)
            day_week = data_time.strftime("%w")
            if int(day_week) in range(1, 6):
                if time in filters_weekday:
                    cprint(f"Начало обновления в {time}!", "light_blue")
                    update_prices(args_command=args_command)
            elif day_week == "6":
                if time in filters_weekends:
                    cprint(f"Начало обновления в {time}!", "light_blue")
                    update_prices(args_command=args_command)


if __name__ == "__main__":
    print(
        f"""Версия программы: {__version__}
Версия parser: {str_mobile.__version__}
Версия OzonSeller: {OzonSeller_api.__version__}"""
    )
    Main()
