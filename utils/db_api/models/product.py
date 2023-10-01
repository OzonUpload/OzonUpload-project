from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Product(Base):
    """Модель товара"""

    __tablename__ = "products"

    Id = Column(Integer, primary_key=True)
    Article = Column(Integer, nullable=False)
    VendorId = Column(Integer, nullable=False)
    VendorUrl = Column(String(300), nullable=False)
    ProductId = Column(Integer, nullable=True)
    WarehouseName = Column(String, nullable=True)
