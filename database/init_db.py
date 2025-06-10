# init_db.py
from database.db import sync_engine
from database.models import Base

if __name__ == "__main__":
    Base.metadata.drop_all(bind=sync_engine)  # ← очищает БД
    Base.metadata.create_all(bind=sync_engine)