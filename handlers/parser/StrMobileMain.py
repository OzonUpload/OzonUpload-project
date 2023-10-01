import datetime
from pathlib import Path
from pprint import pprint

import str_mobile
import utils.db_api.handlers.product as db_products
from handlers.ozon import OzonHandler, OzonMain
from handlers.Update.update_stocks import create_null_products, custom_parametrs
from MyFormatter.handlers.int_bool_to_text import int_bool_to_text as ibtt
from prompt_toolkit import PromptSession
from prompt_toolkit import print_formatted_text as print
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.history import FileHistory
from str_mobile.utils.db_api.Category.handlers import settings_price, settings_stock
from str_mobile.models.product import Product
from termcolor import cprint
from tqdm import tqdm
from utils.config import city, notification, sklads_names, style
from utils.decorators import mult_threading, notification_bot, timer
from utils.get_data import get_data

from utils.create_dir import PATH_HISTORY


class StrMobileMain:
    """Класс парсера сайта str-mobile.com"""

    def __init__(self):
        self.session = PromptSession(
            history=FileHistory(
                PATH_HISTORY / Path(f"history_{self.__class__.__name__}")
            )
        )
        self.dict_parser = {
            "products": {"ids": [], "articles": [], "codes": []},
            "categories": [],
        }
        self.worked_update_stocks = False
        self.worked_update_prices = False
        self.format_output = "Text"
        self.ozon_main = OzonMain()

    def __call__(self):
        message = [
            ("class:project", "parser"),
            ("class:at", ":"),
            ("class:module", "str_mobile"),
            ("class:sign_more", ">"),
        ]
        commands_completer = NestedCompleter.from_nested_dict(
            {
                "add": {
                    "product": {"id": None, "article": None, "code": None},
                    "category": None,
                    "category_settings": {"price": None, "stock": None, "full": None},
                },
                "get": {
                    "products": {"ids": None, "articles": None, "codes": None},
                    "categories": None,
                    "category_settings": None,
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
                    "product": {"id": None, "article": None, "code": None},
                    "category": None,
                    "list": {
                        "products": {"ids": None, "articles": None, "codes": None},
                        "categories": None,
                    },
                    "full": None,
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
                "set": {"format": {"Text": None, "Dict": None, "OzonExcel": None}},
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
                # update
                case "update", "category", category_code:
                    products = self.update_category(category_code=category_code)
                    if len(products) > 0:
                        [print(product) for product in products]
                case "update", "product", type_product_name, product_name:
                    ProductInfo = self.update_product(
                        type_product_name=type_product_name, product_name=product_name
                    )
                    if ProductInfo.Product:
                        print(ProductInfo.Text)
                case "update", "full":
                    products = self.update_full()
                    cprint(
                        f"Обновлено в базу {len(products)} товаров с str-mobile!",
                        "light_blue",
                    )
                case "update":
                    products = self.update()
                    cprint(
                        f"Обновлено в базу {len(products)} товаров с str-mobile!",
                        "light_blue",
                    )
                case "update", "list", "products", type_products_names:
                    products = self.get_list_info_products(
                        type_products_names=type_products_names
                    )
                    if len(products) > 0:
                        [print(product.Text) for product in products]
                    cprint(
                        f"Обновлено в базу {len(products)} товаров с str-mobile!",
                        "light_blue",
                    )
                case "update", "list", "categories":
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
                case "set", "format", format:
                    self.format_output = format
                    cprint(f"Текущий формат: {format}")
                case "get", "format":
                    cprint(f"Текущий формат: {format}")
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
                case "get", "category_settings", category_code:
                    print(f"Категория: {category_code}")
                    if current_settings_price := settings_price.get(
                        CategoryId=category_code
                    ):
                        print(
                            f"Цена логистики: {current_settings_price.PriceLogistics}\nПроцент накрутки: {current_settings_price.PercentCheating}"
                        )
                    if current_settings_stock := settings_stock.get(
                        CategoryId=category_code
                    ):
                        print(
                            f'Работа фильтра отстатков: {ibtt(int(current_settings_stock.WorkedFilter),"ru")}\nМинимальный остаток: {current_settings_stock.MinStock}'
                        )
                    else:
                        cprint(
                            "Информациия не была найдена в базе данных.", "light_red"
                        )
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
                case "add", "category_settings", type_settings:
                    self.add_category_settings(type_settings=type_settings)
                # clear
                case "clear", "products", type_products_names:
                    self.dict_parser["products"][type_products_names] = []
                    cprint("Список товаров очищен!", "light_blue")
                case "clear", "categories":
                    self.dict_parser["categories"] = []
                    cprint("Список категорий очищен!", "light_blue")
                case _:
                    cprint("Вы ввели нерпавильную команду!", "light_red")

    def add_category_settings(self, type_settings: str):
        """Добавление настроек категории"""

        def add_price():
            """Добавление настроек цены"""

            while True:
                price_logistics = input("Введите цену логистики: ")
                if not price_logistics.isdigit():
                    cprint("Введите  число!", "light_red")
                else:
                    break

            while True:
                percent_cheating = input("Введите процент накрутки: ")
                if not percent_cheating.isdigit():
                    cprint("Введите  число!", "light_red")
                else:
                    break

            if settings_price.add(
                CategoryId=category_code,
                PriceLogistics=price_logistics,
                PercentCheating=percent_cheating,
            ):
                cprint("Настройки сохранены.", "light_blue")

        def add_stock():
            """Добавление настроек остатков"""

            while True:
                worked_filter = input("Включить фильтр выгрузки остатка? Да/Нет: ")
                if worked_filter not in ["Да", "Нет"]:
                    cprint("Введите Да или  Нет!")
                else:
                    break
            if worked_filter == "Да":
                while True:
                    min_stock = input("Введите количество минимального отстатка: ")
                    if not min_stock.isdigit():
                        cprint("Введите  число!", "light_red")
                    else:
                        break
            else:
                min_stock = 0

            if settings_stock.add(
                CategoryId=category_code, WorkedFilter=worked_filter, MinStock=min_stock
            ):
                cprint("Настройки сохранены.", "light_blue")

        category_code = input("Добавление настроек для категории: ")

        if type_settings == "price":
            add_price()
        elif type_settings == "stock":
            add_stock()
        elif type_settings == "full":
            add_price()
            add_stock()

    @timer
    def update(self):
        """Обновление информации о всех товарах"""

        products = str_mobile.update()
        [
            db_products.add_product(
                Article=product.article, VendorId=product.id, VendorUrl=product.url
            )
            for product in products
        ]
        return products

    @timer
    def update_full(self):
        """Обновление товаров всех категорий"""

        products = str_mobile.update_full()
        [
            db_products.add_product(
                Article=product.article, VendorId=product.id, VendorUrl=product.url
            )
            for product in products
        ]
        return products

    def update_product(self, type_product_name: str, product_name: str):
        """Обновление товара по одному из типу наименований: id, artikyl, code"""

        product_info = db_products.get_product_type_name(
            type_product_name=type_product_name, product_name=product_name
        )
        if product_info:
            code_product = product_info.VendorUrl
        elif type_product_name == "code":
            code_product = product_name
        else:
            ProductInfo = type(
                "ProductInfo",
                (object,),
                {
                    "Product": None,
                    "Text": f"Товар '{product_name}' не был  найден в базе данных!",
                },
            )
            cprint(ProductInfo.Text, "light_red")
            return ProductInfo

        ProductInfo = str_mobile.update_product(code_product=code_product)
        product: Product = ProductInfo.Product

        if product is not None:
            db_products.add_product(
                Article=product.article,
                VendorId=product.id,
                VendorUrl=product.url,
                CategoryId=product.category_id,
            )
            db_products.update_warehouse_product(
                VendorId=product.id,
                WarehouseName=sklads_names[product.sklad].WarehouseName,
            )
        else:
            self.update_category(category_code=product_info.CategoryId)
            ProductInfo = self.update_product(type_product_name, product_name)
        return ProductInfo

    def update_category(self, category_code: str):
        """Обновление товаров категории по номеру категории"""

        products = str_mobile.update_category(category_code=category_code)
        [
            db_products.add_product(
                Article=product.Product.article,
                VendorId=product.Product.id,
                VendorUrl=product.Product.url,
                CategoryId=product.Product.category_id
            )
            for product in products
            if product.Product is not None
        ]
        cprint(
            f"Обновлено в базу {len(products)} товаров с str-mobile!",
            "light_blue",
        )
        match self.format_output:
            case "Text":
                products = [product.Text for product in products]
        return products

    def add_product(self, type_product_name: str, args_command: list[str]):
        """Добавление товара/товаров в список товаров по типам: ids, artikles, codes"""

        match type_product_name:
            case "id":
                list_products = self.dict_parser["products"]["ids"]
                for arg in args_command:
                    if not arg.isdigit():
                        cprint("Id должен состоять только из чисел!", "light_red")
                        return
            case "article":
                list_products = self.dict_parser["products"]["articles"]
                for arg in args_command:
                    if not arg.isdigit():
                        cprint("Article должен состоять только из чисел!", "light_red")
                        return
            case "code":
                list_products = self.dict_parser["products"]["codes"]

        [list_products.append(arg) for arg in args_command]
        cprint(
            f"Вы добавили код продукта! Текущий список содержит: {len(list_products)} кодов товаров.",
            "light_blue",
        )

    def get_list_info_products(self, type_products_names):
        """Получение списка информаций о товарах"""

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

        text = f"Обновление остатков, {len(updates)-len(errors)}/{len(products_ozon)} товаров прошло успешно!"

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

        text = f"Обновление цен, {len(updates)-len(errors)}/{len(products_ozon)} товаров прошло успешно!"

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
