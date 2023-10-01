from pathlib import Path
import re
import traceback

from sqlalchemy import create_engine
from sqlalchemy import exc as sqlalchemy_exc
from sqlalchemy.orm import Session
from utils.create_dir import PATH_PROJECT

from utils.db_api.models.product import Product

engine = create_engine(f'sqlite:///{PATH_PROJECT/Path("data.db")}')
session = Session(engine)


def get_products_list():
    """Получение списка всех товаров"""

    products = session.query(Product).all()
    return products


def get_products_list_ozon():
    """Получение списка товаров с ProductId"""

    products: list[Product] = (
        session.query(Product).filter(Product.ProductId.is_not(None)).all()
    )
    return products


def get_product(VendorId: int = None, Article: int = None, VendorUrl: str = None):
    """Получение информации о товаре по: VendorId, Artivcle, VendorUrl"""

    try:
        if VendorId:
            product = session.query(Product).filter(Product.VendorId == VendorId).one()
        elif Article:
            product = session.query(Product).filter(Product.Article == Article).one()
        elif VendorUrl:
            product = (
                session.query(Product).filter(Product.VendorUrl == VendorUrl).one()
            )
        return product
    except:
        return False


def get_product_type_name(type_product_name: str, product_name: str):
    """Получение информации о товаре по типу наименования: id, article, code"""
    match type_product_name:
        case "id":
            product = get_product(VendorId=product_name)
        case "article":
            product = get_product(Article=product_name)
        case _:
            product = get_product(VendorUrl=product_name)

    return product


def update_warehouse_product(VendorId: int, WarehouseName: str):
    """Обновление склада у товара по VendorId"""

    try:
        product = session.query(Product).filter(Product.VendorId == VendorId).one()
        if product.ProductId is not None and product.WarehouseName is None:
            product.WarehouseName = WarehouseName
            session.add(product)
            session.commit()
            return True
        else:
            return False
    except sqlalchemy_exc.NoResultFound:
        print("\n" + VendorId, WarehouseName)
        return False
    except Exception as e:
        traceback.print_exception(e)
        return False


def update_product(ArticleOzon: int, ProductId: int, WarehouseName: str):
    """ "Обновление информации о товаре по ArticleOzon"""

    VendorId = re.findall(r"([^())]+)\)", ArticleOzon)[0]

    try:
        product = session.query(Product).filter(Product.VendorId == VendorId).one()
        product.ProductId = ProductId
        if product.WarehouseName is None:
            product.WarehouseName = WarehouseName
        session.add(product)
        session.commit()
        return True
    except sqlalchemy_exc.NoResultFound:
        print("\n" + ArticleOzon, ProductId)
        return False
    except Exception as e:
        traceback.print_exception(e)
        print("\n" + ArticleOzon, ProductId)
        return False


def add_product(Article: int, VendorId: int, VendorUrl: str):
    """Добавление информации о товаре"""

    try:
        product = session.query(Product).filter(Product.VendorId == VendorId).one()
        
        if product.VendorUrl != VendorUrl:
            product.VendorUrl = VendorUrl
            session.add(product)
            session.commit()
            return True
        else:
            return False
        
    except sqlalchemy_exc.NoResultFound:
        product = Product(Article=Article, VendorId=VendorId, VendorUrl=VendorUrl)
        session.add(product)
        session.commit()
        return True
    except Exception as e:
        traceback.print_exception(e)
        return False
    
def delete_product(ProductId: int):
    try:
        product = session.query(Product).filter(Product.ProductId == ProductId).one()
        session.delete(product)
        session.commit()
        return True
    except:
        return False
