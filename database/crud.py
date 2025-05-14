from sqlalchemy import select, update, delete
from database.db import AsyncSessionLocal
from database.models import User, Prompt, Channel

# 👤 Создание пользователя (если не существует)
async def get_or_create_user(user_id: int, username: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if user:
            return user
        user = User(id=user_id, username=username)
        session.add(user)
        await session.commit()
        return user

# 🧠 Получение активного промпта
async def get_active_prompt(user_id: int) -> str:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Prompt).where(Prompt.user_id == user_id, Prompt.is_active == True)
        )
        prompt = result.scalars().first()
        return prompt.text if prompt else "Сгенерируй пример поста."

# ✍️ Сохранение нового промпта (старый станет неактивным)
async def set_active_prompt(user_id: int, text: str):
    async with AsyncSessionLocal() as session:
        await session.execute(
            update(Prompt)
            .where(Prompt.user_id == user_id, Prompt.is_active == True)
            .values(is_active=False)
        )
        session.add(Prompt(user_id=user_id, text=text, is_active=True))
        await session.commit()

# 📡 Добавить канал пользователю
async def add_channel(user_id: int, chat_id: int, title: str):
    async with AsyncSessionLocal() as session:
        channel = Channel(id=chat_id, title=title, owner_id=user_id)
        session.add(channel)
        await session.commit()

# 📋 Получить каналы пользователя
async def get_user_channels(user_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Channel).where(Channel.owner_id == user_id)
        )
        return result.scalars().all()

# 🗑️ Удалить канал
async def delete_channel(user_id: int, chat_id: int):
    async with AsyncSessionLocal() as session:
        await session.execute(
            delete(Channel).where(Channel.owner_id == user_id, Channel.id == chat_id)
        )
        await session.commit()

# 📋 Получить все промпты пользователя (новые сверху)
async def get_all_prompts(user_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Prompt)
            .where(Prompt.user_id == user_id)
            .order_by(Prompt.id.desc())
        )
        return result.scalars().all()

# 🟢 Сделать промпт активным
async def activate_prompt(prompt_id: int, user_id: int):
    async with AsyncSessionLocal() as session:
        # Снимаем активный
        await session.execute(
            update(Prompt)
            .where(Prompt.user_id == user_id)
            .values(is_active=False)
        )
        # Назначаем новый
        await session.execute(
            update(Prompt)
            .where(Prompt.id == prompt_id, Prompt.user_id == user_id)
            .values(is_active=True)
        )
        await session.commit()

# ❌ Удалить промпт
async def delete_prompt(prompt_id: int, user_id: int):
    async with AsyncSessionLocal() as session:
        await session.execute(
            delete(Prompt)
            .where(Prompt.id == prompt_id, Prompt.user_id == user_id)
        )
        await session.commit()
