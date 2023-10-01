from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from utils.create_dir import PATH_PROJECT

from utils.db_api.models.warehouse import Warehouse

engine = create_engine(f'sqlite:///{PATH_PROJECT/Path("data.db")}')
session = Session(engine)


def get_warehouses_list():
    """Получение списка складов ozon"""

    warehouses = session.query(Warehouse).all()

    return warehouses


def get_warehouse(WarehouseName: str = None, WarehouseId: int = None):
    """Получение склада по WarehouseName, WarehouseId"""

    try:
        if WarehouseName:
            warehouse = (
                session.query(Warehouse)
                .filter(Warehouse.WarehouseName == WarehouseName)
                .one()
            )
        elif WarehouseId:
            warehouse = (
                session.query(Warehouse)
                .filter(Warehouse.WarehouseId == WarehouseId)
                .one()
            )
        return warehouse
    except:
        return False


def add_warehouse(WarehouseName: str, WarehouseId: int):
    """Добавление информации о складе"""

    try:
        session.query(Warehouse).filter(Warehouse.WarehouseId == WarehouseId).one()
    except:
        warehouse = Warehouse(WarehouseName=WarehouseName, WarehouseId=WarehouseId)

        session.add(warehouse)
        session.commit()
