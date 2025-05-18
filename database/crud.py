from sqlalchemy import select, update, delete
from database.db import AsyncSessionLocal
from database.models import User, Prompt, Channel
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Message

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


async def get_active_prompt(session: AsyncSession, user_id: int) -> Prompt | None:
    result = await session.execute(
        select(Prompt).where(Prompt.user_id == user_id, Prompt.is_active == True)
    )
    return result.scalar_one_or_none()

# ✍️ Сохранение нового промпта (старый станет неактивным)
async def set_active_prompt(session: AsyncSession, user_id: int, text: str):
    await session.execute(
        update(Prompt)
        .where(Prompt.user_id == user_id, Prompt.is_active == True)
        .values(is_active=False)
    )
    session.add(Prompt(user_id=user_id, text=text, is_active=True))
    await session.commit()

# 📡 Добавить канал пользователю
async def add_channel(owner_id: int | None, title: str, channel_id: int):
    if owner_id is None:
        print("⚠️ Пустой owner_id — не сохраняем.")
        return

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Channel).where(Channel.owner_id == owner_id, Channel.channel_id == channel_id)
        )
        existing = result.scalar_one_or_none()

        if existing:
            print("⚠️ Канал уже существует.")
            return

        channel = Channel(owner_id=owner_id, title=title, channel_id=channel_id)
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
async def delete_channel(channel_id: int, owner_id: int):
    async with AsyncSessionLocal() as session:
        await session.execute(
            delete(Channel).where(Channel.id == channel_id, Channel.owner_id == owner_id)
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


# 💬 Добавить сообщение
async def add_message(session: AsyncSession, user_id: int, role: str, content: str):
    session.add(Message(user_id=user_id, role=role, content=content))
    await session.commit()

# 🧠 Получить последние 10 сообщений
async def get_last_messages(session: AsyncSession, user_id: int, limit: int = 10) -> list[Message]:
    result = await session.execute(
        select(Message)
        .where(Message.user_id == user_id)
        .order_by(Message.id.desc())
        .limit(limit)
    )
    return list(reversed(result.scalars().all()))
