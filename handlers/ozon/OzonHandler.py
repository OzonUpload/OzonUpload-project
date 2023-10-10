from pprint import pprint
import OzonSeller_api
from str_mobile.models.product import Product as ParserProduct
from tabulate import tabulate
from termcolor import cprint

import utils.db_api.handlers.product as db_products
import utils.db_api.handlers.warehouse as db_warehouses
from utils.config import sklads_names
from loguru import logger
from MyFunc import iprint


def check_stocks(offer_id: str, stocks_products: dict):
    """Проверка остатков на FBO и Наличие"""
    
    res = True
    current_stock_fbo_product = False
    current_stock_product = False

    stocks_product = stocks_products[offer_id]
    if not stocks_product.get("Наличие"):
        logger.warning(f"{offer_id} не найден на складе Наличие.")
    else:
        if int(stocks_product["Наличие"]["present"]) > 0:
            current_stock_product = stocks_product["Наличие"]
            res = False

    if not stocks_product.get("fbo"):
        logger.warning(f"{offer_id} не найден на складе fbo.")
    else:
        if int(stocks_product["fbo"]["present"]) > 0:
            current_stock_fbo_product = stocks_product["fbo"]
            res = False  

    return res, current_stock_product, current_stock_fbo_product

def print_stocks(current_stocks_fbo_products: dict, current_stocks_products: dict):
    """Вывод таблиц остатков на FBO и Наличие"""
    
    # таблица остатков на FBO
    if len(current_stocks_fbo_products) > 0:
        head = ["offer_id", "Всего", "Зарезервировано"]
        data = []
        for offer_id, stocks in current_stocks_fbo_products.items():
            data.append([offer_id, stocks["present"], stocks["reserved"]])
        cprint(f"Товаров на FBO: {len(current_stocks_fbo_products)}", "light_yellow")
        print("Остатки товаров на FBO:")
        print(tabulate(data, headers=head, tablefmt="grid"))

    # Таблица остатков на Наличие
    if len(current_stocks_products) > 0:
        head = ["offer_id", "Всего", "Зарезервировано"]
        data = []
        for offer_id, stocks in current_stocks_products.items():
            data.append([offer_id, stocks["present"], stocks["reserved"]])
        cprint(f"Товаров на Наличие: {len(current_stocks_products)}", "light_yellow")
        print("Остатки товаров на Наличие:")
        print(tabulate(data, headers=head, tablefmt="grid"))

def upload_products_stocks(
    products_parser: list[ParserProduct],
    stocks_products: dict,
    set_stock: int = None,
    set_warehouse_name: str = None,
):
    """Выгрузка остатка товаров на ozon"""

    def append_product(
        object: list, offer_id: str, product_id: int, stock: int, warehouse_id: str
    ):
        """Добавление информации о товаре в список"""

        object.append(
            {
                "offer_id": offer_id,
                "product_id": product_id,
                "stock": stock,
                "warehouse_id": warehouse_id,
            }
        )

    products_warehouses = {"ST": [], "Absol": [], "MSK": []}

    current_stocks_fbo_products = {}
    current_stocks_products = {}

    for product_info in products_parser:
        product = product_info.Product
        if (info_product := db_products.get_product(VendorId=product.id)) and product:
            if info_product.ProductId is not None:
                article = info_product.Article
                vendor_id = info_product.VendorId
                offer_id = f"{article} ({vendor_id})"

                res, current_stock_product, current_stock_fbo_product = check_stocks(
                    offer_id, stocks_products
                )

                if current_stock_product:
                    current_stocks_products[offer_id] = current_stock_product
                if current_stock_fbo_product:
                    current_stocks_fbo_products[offer_id] = current_stock_fbo_product

                if not res:
                    continue

                if set_warehouse_name:
                    warehouse_product = db_warehouses.get_warehouse(
                        WarehouseName=set_warehouse_name
                    )
                else:
                    warehouse_product = db_warehouses.get_warehouse(
                        WarehouseName=info_product.WarehouseName
                    )

                if set_stock != None:
                    stock = set_stock
                else:
                    stock = product.col

                for sklad in sklads_names.values():
                    sklad_name = sklad.WarehouseName
                    if sklad.WarehouseName == warehouse_product.WarehouseName:
                        append_product(
                            object=products_warehouses[sklad_name],
                            offer_id=offer_id,
                            product_id=info_product.ProductId,
                            stock=stock,
                            warehouse_id=sklad.WarehouseId,
                        )
                    else:
                        append_product(
                            object=products_warehouses[sklad_name],
                            offer_id=offer_id,
                            product_id=info_product.ProductId,
                            stock=0,
                            warehouse_id=sklad.WarehouseId,
                        )

    products = []
    for products_warehouse in products_warehouses.values():
        products += products_warehouse
    
    print_stocks(current_stocks_fbo_products, current_stocks_products)

    if len(products) > 0:
        result = OzonSeller_api.upload_products_stocks(products)
    else:
        return [], {}

    updates = {}
    if result is not None:
        for product in result:
            updates[product["offer_id"]] = {
                "updated": product["updated"],
                "errors": product["errors"],
            }

        errors = [
            {"offer_id": offer_id, "errors": info_product["errors"][0]}
            for offer_id, info_product in updates.items()
            if info_product["updated"] == False
        ]

        return errors, updates

    return [], {}


def upload_products_prices(products_parser: list[ParserProduct], stocks_products: dict):
    """Выгрузка цен товаров на ozon"""

    current_stocks_fbo_products = {}
    current_stocks_products = {}
    products = []
    for product_info in products_parser:
        product = product_info.Product
        if info_product := db_products.get_product(VendorId=product.id):
            if info_product.ProductId is not None:
                article = info_product.Article
                vendor_id = info_product.VendorId
                offer_id = f"{article} ({vendor_id})"
                price = product.product_price
                min_price = product.min_price
                old_price = product.discount_price
                data_product = {
                    "auto_action_enabled": "ENABLED",
                    "currency_code": "RUB",
                    "min_price": str(min_price),
                    "offer_id": str(offer_id),
                    "old_price": str(old_price),
                    "price": str(price),
                    "product_id": info_product.ProductId,
                }

                res, current_stock_product, current_stock_fbo_product = check_stocks(
                    offer_id, stocks_products
                )

                if current_stock_product:
                    current_stocks_products[offer_id] = current_stock_product
                if current_stock_fbo_product:
                    current_stocks_fbo_products[offer_id] = current_stock_fbo_product

                if not res:
                    continue

                products.append(data_product)
    
    print_stocks(current_stocks_fbo_products, current_stocks_products)

    if len(products) > 0:
        result = OzonSeller_api.upload_products_prices(products=products)
    else:
        return [], {}
    
    updates = {}
    if result is not None:
        for product in result:
            updates[product["offer_id"]] = {
                "updated": product["updated"],
                "errors": product["errors"],
            }

        errors = [
            {"offer_id": offer_id, "errors": info_product["errors"][0]}
            for offer_id, info_product in updates.items()
            if info_product["updated"] == False
        ]

        return errors, updates

    return [], {}
