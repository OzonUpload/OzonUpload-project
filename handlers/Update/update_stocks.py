from dataclasses import dataclass
from loguru import logger

import str_mobile
from termcolor import cprint
from tqdm import tqdm

from handlers.ozon import OzonHandler, OzonMain
from utils.config import notification
from utils.db_api.handlers import product as db_products
from utils.decorators import notification_bot, timer


@dataclass
class ProductNullStock:
    """Класс товара не в наличии"""

    id: int
    col: int = 0


def create_null_products(list_products: list[str], type_products_names):
    """Создание списка товаров не в наличии"""

    products_parser = []
    for arg in list_products:
        match type_products_names[:-1]:
            case "id":
                id = db_products.get_product(VendorId=arg).VendorId
            case "article":
                id = db_products.get_product(Article=arg).VendorId
            case "code":
                id = db_products.get_product(VendorUrl=arg).VendorId

        product = ProductNullStock(id)
        products_parser.append(product)

    return products_parser


def custom_parametrs(args_command: list[str]):
    """Получение параметров выгрузки: set_stocks, set_warehouse_name"""

    set_stocks = None
    set_warehouse_name = None
    if len(args_command) > 1:
        match args_command:
            case "/s", value, *args_command:
                set_stocks = int(value)

                if len(args_command) > 1:
                    match args_command:
                        case "/w", value:
                            set_warehouse_name = str(value)
                        case _:
                            cprint("Неправильные параметры команды!", "light_red")
                            return False

            case "/w", value, *args_command:
                set_warehouse_name = str(value)

                if len(args_command) > 1:
                    match args_command:
                        case "/s", value, *args_command:
                            set_stocks = int(value)
                        case _:
                            cprint("Неправильные параметры команды!", "light_red")
                            return False
            case _:
                cprint("Неправильные параметры команды!", "light_red")
                return False
    elif len(args_command) == 1:
        cprint("Недостаточно параметров команды!", "light_red")
        return False

    return set_stocks, set_warehouse_name


@timer
@notification_bot(notification)
def update_stocks(args_command: list[str]):
    """Обновление остатка товаров"""

    ozon_main = OzonMain()
    logger.info("Выпонение обновления остатков...")

    match args_command:
        case "full", *args_command:
            set_stocks, set_warehouse_name = custom_parametrs(args_command=args_command)
            if set_stocks != None:
                products_parser = create_null_products(
                    list_products=[
                        product_ozon.VendorId for product_ozon in products_ozon
                    ],
                    type_products_names="ids",
                )
            else:
                products_parser = [
                    product
                    for product in [
                        str_mobile.update_product(code_product=product_ozon.VendorUrl)
                        for product_ozon in tqdm(
                            products_ozon,
                            desc="Обновление товаров с ProductId",
                            position=0,
                            colour="green",
                            ascii=True,
                            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}",
                        )
                    ]
                ]
        case "category", category_code, *args_command:
            set_stocks, set_warehouse_name = custom_parametrs(args_command=args_command)
            products_parser = str_mobile.update_category(category_code=category_code)
        case "product", type_product_name, product_name, *args_command:
            set_stocks, set_warehouse_name = custom_parametrs(args_command=args_command)
            if set_stocks != None:
                products_parser = create_null_products(
                    list_products=[product_name], type_products_names=type_product_name
                )
            else:
                product_info = db_products.get_product_type_name(
                    type_product_name=type_product_name, product_name=product_name
                )
                if product_info:
                    code_product = product_info.VendorUrl
                else:
                    logger.warning(
                        f"Товар не был  найден в базе данных! {product_name}"
                    )
                    return False

                product = str_mobile.update_product(code_product=code_product)

                if product is not None:
                    products_parser = [product]
                else:
                    logger.error("Ошибка получения информации с сайта!")
                    return False
        case _:
            logger.warning("Вы ввели нерпавильную команду!")
            return False

    if len(products_parser) == 0:
        logger.warning("Товаров на выгрузку не собрано.")
        return False

    ozon_main.update_products()
    products_ozon = db_products.get_products_list_ozon()

    errors, updates = OzonHandler.upload_products_stocks(
        products_parser=products_parser,
        stocks_products=ozon_main.get_stocks_products(),
        set_stock=set_stocks,
        set_warehouse_name=set_warehouse_name,
    )

    text = f"Обновление остатков {len(updates)-len(errors)}/{len(products_ozon)} товаров прошло успешно!"

    return text, errors
