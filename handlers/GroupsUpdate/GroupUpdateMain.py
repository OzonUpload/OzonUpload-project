import datetime
from pathlib import Path

import str_mobile
import utils.db_api.handlers.product as db_products
from handlers.ozon import OzonHandler, OzonMain
from handlers.parser.StrMobileMain import StrMobileMain
from handlers.Update.update_stocks import create_null_products, custom_parametrs
from prompt_toolkit import PromptSession
from prompt_toolkit import print_formatted_text as print
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.history import FileHistory
from termcolor import cprint
from tqdm import tqdm
from utils.config import city, notification, style
from utils.decorators import mult_threading, notification_bot, timer
from utils.get_data import get_data

from utils.create_dir import PATH_HISTORY_GROUPS_UPDATE


class GroupUpdateMain:
    update_product = StrMobileMain.update_product
    update_category = StrMobileMain.update_category
    add_product = StrMobileMain.add_product

    def __init__(self, group_name: str, dict_parser: dict):
        self.group_name = group_name
        self.session = PromptSession(
            history=FileHistory(
                PATH_HISTORY_GROUPS_UPDATE
                / Path(f"history_{self.__class__.__name__}_{group_name}")
            )
        )
        self.dict_parser = dict_parser
        self.worked_update_stocks = False
        self.worked_update_prices = False
        self.ozon_main = OzonMain()

    def __call__(self):
        message = [
            ("class:project", self.group_name),
            ("class:at", ":"),
            ("class:sign_more", ">"),
        ]
        commands_completer = NestedCompleter.from_nested_dict(
            {
                "add": {
                    "product": {"id": None, "article": None, "code": None},
                    "category": None,
                },
                "get": {
                    "products": {"ids": None, "articles": None, "codes": None},
                    "categories": None,
                },
                "update": {
                    "stocks": {
                        "products": {"ids": None, "articles": None, "codes": None},
                        "categories": None,
                    },
                    "prices": {
                        "products": {"ids": None, "articles": None, "codes": None},
                        "categories": None,
                    },
                    "products": {"ids": None, "articles": None, "codes": None},
                    "categories": None,
                },
                "start": {
                    "update": {
                        "stocks": {
                            "products": {
                                "ids": None,
                                "articles": None,
                                "codes": None,
                            },
                            "categories": None,
                        },
                        "prices": {
                            "products": {"ids": None, "articles": None, "codes": None},
                            "categories": None,
                        },
                    }
                },
                "stop": {"update": {"stocks": None, "prices": None}},
                "clear": {
                    "products": {"ids": None, "articles": None, "codes": None},
                    "categories": None,
                },
                "exit": None,
            }
        )

        while True:
            text: str = self.session.prompt(
                message=message, style=style, completer=commands_completer
            )

            if text == "exit":
                self.worked_update_stocks = False
                self.worked_update_prices = False
                break
            elif len(text.split(" ")) > 1:
                value = text.split()
            else:
                value = text

            match value:
                case "update", "products", type_products_names:
                    products = self.get_list_info_products(
                        type_products_names=type_products_names
                    )
                    if len(products) > 0:
                        [print(product.Text) for product in products]
                    cprint(
                        f"Обновлено в базу {len(products)} товаров с str-mobile!",
                        "light_blue",
                    )
                case "update", "categories":
                    codes_category = self.dict_parser["categories"]
                    products = []
                    [
                        [
                            products.append(product)
                            for product in self.update_category(
                                category_code=category_code
                            )
                            if product is not None
                        ]
                        for category_code in tqdm(
                            codes_category,
                            desc="Обновление списка категорий",
                            colour="green",
                            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}",
                        )
                    ]
                    cprint(
                        f"Обновлено в базу {len(products)} товаров с str-mobile!",
                        "light_blue",
                    )
                case "update", "stocks", *args_command:
                    self.update_stocks(args_command=args_command)
                case "update", "prices", *args_command:
                    self.update_prices(args_command=args_command)
                # start
                case "start", "update", "stocks", *args_command:
                    self.start_update_stocks(args_command=args_command)
                case "start", "update", "prices", *args_command:
                    self.start_update_prices(args_command=args_command)
                # stop
                case "stop", "update", "stocks":
                    if self.worked_update_stocks:
                        self.worked_update_stocks = False
                        cprint("Остановлено!", "light_blue")
                    else:
                        cprint("Незапущено!", "light_blue")
                case "stop", "update", "prices":
                    if self.worked_update_prices:
                        self.worked_update_prices = False
                        cprint("Остановлено!", "light_blue")
                    else:
                        cprint("Незапущено!", "light_blue")
                # get
                case "get", "products", type_products_names:
                    list_type_products = self.dict_parser["products"][
                        type_products_names
                    ]
                    if len(list_type_products) > 0:
                        print(list_type_products)
                    else:
                        cprint("Список товаров пуст!", "light_blue")
                case "get", "categories":
                    list_categories = self.dict_parser["categories"]
                    if len(list_categories) > 0:
                        print(list_categories)
                    else:
                        cprint("Список категорий пуст!", "light_blue")
                # add
                case "add", "product", type_product_name, *args_command:
                    self.add_product(
                        type_product_name=type_product_name, args_command=args_command
                    )
                case "add", "category", *args_command:
                    [self.dict_parser["categories"].append(arg) for arg in args_command]
                    cprint(
                        f'Вы добавили код категории! Текущий список содержит: {len(self.dict_parser["categories"])} кодов категорий.',
                        "light_blue",
                    )
                # clear
                case "clear", "products", type_products_names:
                    self.dict_parser["products"][type_products_names] = []
                    cprint("Список товаров очищен!", "light_blue")
                case "clear", "categories":
                    self.dict_parser["categories"] = []
                    cprint("Список категорий очищен!", "light_blue")
                case _:
                    cprint("Вы ввели нерпавильную команду!", "light_red")

    def get_list_info_products(self, type_products_names: str):
        """Получение списка инфорамации о товарах"""

        dict_list_products = self.dict_parser["products"]

        try:
            dict_list_type_products = dict_list_products[type_products_names]
        except:
            cprint("Неправильно указан тип списка товаров!", "light_red")
            return []

        if len(dict_list_type_products) == 0:
            cprint("Список товаров данного типа пуст!", "light_red")
            return []

        products = [
            product
            for product in [
                self.update_product(
                    type_product_name=type_products_names[:-1],
                    product_name=product_name,
                )
                for product_name in tqdm(
                    dict_list_type_products,
                    desc="Обновление списка товаров",
                    colour="green",
                    ascii=True,
                    bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}",
                )
            ]
            if product.Product is not None
        ]

        return products

    @timer
    @notification_bot(notification)
    def update_stocks(self, args_command: list):
        """Обновление остатка товаров на ozon"""

        print("Выпонение обновления остатков...")

        match args_command:
            case "products", type_products_names, *args_command:
                set_stocks, set_warehouse_name = custom_parametrs(
                    args_command=args_command
                )

                if set_stocks != None:
                    products_parser = create_null_products(
                        list_products=self.dict_parser["products"][type_products_names],
                        type_products_names=type_products_names,
                    )
                else:
                    products_parser = [
                        product.Product
                        for product in self.get_list_info_products(
                            type_products_names=type_products_names
                        )
                    ]
            case "categories", *args_command:
                set_stocks, set_warehouse_name = custom_parametrs(
                    args_command=args_command
                )
                codes_category = self.dict_parser["categories"]
                products_parser = []

                [
                    [
                        products_parser.append(product)
                        for product in str_mobile.update_category(
                            category_code=category_code
                        )
                    ]
                    for category_code in tqdm(
                        codes_category,
                        "Обновление списка категорий",
                        colour="green",
                        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}",
                    )
                ]
            case _:
                cprint("Вы ввели нерпавильную команду!", "light_red")
                return False

        if len(products_parser) == 0:
            return False

        self.ozon_main.update_products()
        products_ozon = db_products.get_products_list_ozon()

        errors, updates = OzonHandler.upload_products_stoks(
            products_parser=products_parser,
            stocks_products=self.ozon_main.get_stocks_products(),
            set_stock=set_stocks,
            set_warehouse_name=set_warehouse_name,
        )

        text = f'Обновление остатков группы "{self.group_name}", {len(updates)-len(errors)}/{len(products_ozon)} товаров прошло успешно!'

        return text, errors

    @timer
    @notification_bot(notification)
    def update_prices(self, args_command: list[str]):
        """Обновление цен товаров на ozon"""

        print("Выпонение обновления цен...")

        match args_command:
            case "products", type_products_names:
                products_parser = [
                    product.Product
                    for product in self.get_list_info_products(
                        type_products_names=type_products_names
                    )
                ]
            case "categories":
                codes_category = self.dict_parser["categories"]
                products_parser = []
                [
                    [
                        products_parser.append(product)
                        for product in str_mobile.update_category(
                            category_code=category_code
                        )
                    ]
                    for category_code in tqdm(
                        codes_category,
                        "Обновление списка категорий",
                        colour="green",
                        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}",
                    )
                ]
            case _:
                cprint("Вы ввели нерпавильную команду!", "light_red")
                return False

        if len(products_parser) == 0:
            return False

        self.ozon_main.update_products()
        products_ozon = db_products.get_products_list_ozon()

        errors, updates = OzonHandler.upload_products_prices(
            products_parser=products_parser
        )

        text = f'Обновление цен группы "{self.group_name}", {len(updates)-len(errors)}/{len(products_ozon)} товаров прошло успешно!'

        return text, errors

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
                    self.update_stocks(args_command=args_command)
            elif day_week == "6":
                if time in filters_weekends:
                    cprint(f"Начало обновления в {time}!", "light_blue")
                    self.update_stocks(args_command=args_command)

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
                    self.update_prices(args_command=args_command)
            elif day_week == "6":
                if time in filters_weekends:
                    cprint(f"Начало обновления в {time}!", "light_blue")
                    self.update_prices(args_command=args_command)
