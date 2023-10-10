from loguru import logger
import str_mobile
from termcolor import cprint
from tqdm import tqdm

from handlers.ozon import OzonHandler, OzonMain
from handlers.parser.StrMobileMain import StrMobileMain
from utils.config import notification
from utils.db_api.handlers import product as db_products
from utils.decorators import notification_bot, timer

str_mobile_main = StrMobileMain()

@timer
@notification_bot(notification)
def update_prices(args_command: list[str]):
    """Обновление цен товаов на озон"""

    logger.info("Выпонение обновления цен...")

    ozon_main = OzonMain()

    match args_command:
        case "full", *args_command:
            products_parser = [
                product
                for product in [
                    str_mobile_main.update_product(
                        type_product_name="id", product_name=product_ozon.VendorId
                    )
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
            products_parser = str_mobile.update_category(category_code=category_code)
        case "product", type_product_name, product_name, *args_command:
            product_info = db_products.get_product_type_name(
                type_product_name=type_product_name, product_name=product_name
            )
            if product_info:
                code_product = product_info.VendorUrl
            else:
                logger.warning("Товар не был  найден в базе данных!")
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

    errors, updates = OzonHandler.upload_products_prices(
        products_parser=products_parser, 
        stocks_products=ozon_main.get_stocks_products()
    )

    text = f"Обновление цен {len(updates)-len(errors)}/{len(products_ozon)} товаров прошло успешно!"

    return text, errors
