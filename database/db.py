import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine  # ⬅️ для sync engine (create_all)

from contextlib import asynccontextmanager

@asynccontextmanager
async def get_async_session():
    async with AsyncSessionLocal() as session:
        yield session

# ⬇ Путь до БД
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, "db.sqlite3")
DATABASE_URL = f"sqlite+aiosqlite:///{DATABASE_PATH}"

# 🔄 Async Engine для бота
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# 📦 Общая база
Base = declarative_base()

# 🧱 Sync engine только для init_db
SYNC_DATABASE_URL = f"sqlite:///{DATABASE_PATH}"  # без aiosqlite
sync_engine = create_engine(SYNC_DATABASE_URL, echo=False)
# ✅ Экспорт для crud
async_session = AsyncSessionLocal