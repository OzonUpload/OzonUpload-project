from pathlib import Path
from sqlalchemy import create_engine
from utils.create_dir import PATH_PROJECT

from utils.db_api.models import product, warehouse

engine = create_engine(f'sqlite:///{PATH_PROJECT/Path("data.db")}')

warehouse.Base.metadata.create_all(engine)
product.Base.metadata.create_all(engine)
