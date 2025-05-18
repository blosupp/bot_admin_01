# database/init_db.py
from database.db import Base, sync_engine
from database import models  # подтягивает все модели

Base.metadata.create_all(bind=sync_engine)

print("✅ Таблицы успешно созданы!")
