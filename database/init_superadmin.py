# init_superadmin.py

import asyncio
from database.db import async_session
from database.models import User

SUPERADMIN_ID = 1143201422  # 👈 сюда вставь свой Telegram ID
SUPERADMIN_USERNAME = "blosup08"  # 👈 сюда свой username (без @)

async def create_superadmin():
    async with async_session() as session:
        existing = await session.execute(
            User.__table__.select().where(User.id == SUPERADMIN_ID)
        )
        if existing.scalar_one_or_none():
            print("Суперадмин уже существует.")
            return

        user = User(
            id=SUPERADMIN_ID,
            username=SUPERADMIN_USERNAME,
            role="superadmin"
        )
        session.add(user)
        await session.commit()
        print("✅ Суперадмин создан.")

if __name__ == "__main__":
    asyncio.run(create_superadmin())
