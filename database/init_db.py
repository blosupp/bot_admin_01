# init_db.py
from database.models import Base
from database.db import sync_engine

if __name__ == "__main__":
    Base.metadata.create_all(bind=sync_engine)
    print("✅ База создана заново")