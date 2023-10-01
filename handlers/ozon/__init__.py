from pathlib import Path

import OzonSeller_api
import utils.db_api.handlers.product as db_products
import utils.db_api.handlers.warehouse as db_warehouses
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.history import FileHistory
from termcolor import cprint
from tqdm import tqdm
from utils.config import style

from utils.create_dir import PATH_HISTORY


class OzonMain:
    def __init__(self):
        self.session = PromptSession(
            history=FileHistory(
                PATH_HISTORY / Path(f"history_{self.__class__.__name__}")
            )
        )

    def __call__(self):
        message = [("class:project", "ozon"), ("class:sign_more", ">")]
        commands_completer = NestedCompleter.from_nested_dict(
            {
                "get": {"warehouses": None},
                "update": {"warehouses": None, "products": None},
                "exit": None,
            }
        )

        while True:
            text = self.session.prompt(
                message, style=style, completer=commands_completer
            )

            if text.strip() == "exit":
                break
            elif len(text.split(" ")) > 1:
                value = text.split()
            else:
                value = text

            match value:
                case "get", "warehouses":
                    [
                        print(f"{i}) {warehouse.WarehouseName}")
                        for i, warehouse in enumerate(
                            db_warehouses.get_warehouses_list(), start=1
                        )
                    ]
                case "update", "products":
                    self.update_products()
                case "update", "warehouses":
                    self.update_warehouses()
                case _:
                    cprint("Вы ввели нерпавильную команду!", "light_red")

    def update_warehouses(self):
        """Обновление складов на ozon"""

        warehouses = OzonSeller_api.update_warehouses()

        [
            db_warehouses.add_warehouse(
                WarehouseName=warehouse["name"], WarehouseId=warehouse["warehouse_id"]
            )
            for warehouse in warehouses
        ]

        cprint(f"Обновлено в базу {len(warehouses)} складов с ozon!", "light_blue")

    def update_products(self):
        """Обновление товаров на ozon"""

        products = OzonSeller_api.update_products()
        # print((f"ST: {len([product for product in products if product.WarehouseId==db_warehouses.get_warehouse('ST').WarehouseId])}"),
        #       (f"Absol: {len([product for product in products if product.WarehouseId==db_warehouses.get_warehouse('Absol').WarehouseId])}"),
        #       (f"Наличие: {len([product for product in products if product.WarehouseId==db_warehouses.get_warehouse('Наличие').WarehouseId])}"),
        #       (f"Экспресс(такси): {len([product for product in products if product.WarehouseId==db_warehouses.get_warehouse('Экспресс(такси)').WarehouseId])}"))

        col_updated_products = [
            result
            for result in [
                db_products.update_product(
                    ArticleOzon=product.Article,
                    ProductId=product.ProductId,
                    WarehouseName=db_warehouses.get_warehouse(
                        WarehouseId=product.WarehouseId
                    ).WarehouseName,
                )
                for product in tqdm(
                    products,
                    desc="Добавление ProductId в базу",
                    leave=False,
                    colour="blue",
                    bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}",
                )
            ]
            if result != False
        ]

        if len(db_list_products := db_products.get_products_list_ozon()) > len(
            products
        ):
            products_delete = list(
                set([product.ProductId for product in db_list_products])
                ^ set([product.ProductId for product in products])
            )
            for product_id in products_delete:
                db_products.delete_product(product_id)
        cprint(
            f"Обновлено в базу {len(col_updated_products)} товаров с ozon!",
            "light_blue",
        )

    def get_stocks_products(self):
        return OzonSeller_api.current_products_hadlers.current_products.stocks_products
