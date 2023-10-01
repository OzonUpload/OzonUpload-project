from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Warehouse(Base):
    """Модель склада"""

    __tablename__ = "warehouses"
    Id = Column(Integer, primary_key=True)
    WarehouseName = Column(String(300), nullable=False)
    WarehouseId = Column(Integer, nullable=False)
