from sqlalchemy import select, update, delete, desc
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import types
from datetime import datetime

from database.db import AsyncSessionLocal, async_session, get_async_session
from database.models import (
    User, Prompt, Channel, TempPost, Message,
    ScheduledPost, ActionLog
)

# 👤 Создание пользователя (если не существует)
async def get_or_create_user(tg_user: types.User):
    async with get_async_session() as session:
        user = await session.get(User, tg_user.id)
        if not user:
            user = User(
                id=tg_user.id,
                username=tg_user.username,
                role="client"
            )
            session.add(user)
        else:
            user.username = tg_user.username
        await session.commit()
        return user

# 📡 Добавить канал
async def add_channel(owner_id: int | None, title: str, channel_id: int):
    if owner_id is None:
        print("⚠️ Пустой owner_id — не сохраняем.")
        return

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Channel).where(Channel.owner_id == owner_id, Channel.channel_id == channel_id)
        )
        if result.scalar_one_or_none():
            print("⚠️ Канал уже существует.")
            return

        session.add(Channel(owner_id=owner_id, title=title, channel_id=channel_id))
        await session.commit()

# 📋 Получить каналы пользователя
async def get_user_channels(user_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Channel).where(Channel.owner_id == user_id))
        return result.scalars().all()

# 🗑️ Удалить канал
async def delete_channel(channel_id: int, owner_id: int):
    async with AsyncSessionLocal() as session:
        await session.execute(delete(Channel).where(Channel.id == channel_id, Channel.owner_id == owner_id))
        await session.commit()

# 📋 Все промпты пользователя (новые сверху)
async def get_all_prompts(user_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Prompt).where(Prompt.user_id == user_id).order_by(Prompt.id.desc())
        )
        return result.scalars().all()

# 🟢 Сделать промпт активным
async def activate_prompt(prompt_id: int, user_id: int):
    async with AsyncSessionLocal() as session:
        await session.execute(update(Prompt).where(Prompt.user_id == user_id).values(is_active=False))
        await session.execute(
            update(Prompt).where(Prompt.id == prompt_id, Prompt.user_id == user_id).values(is_active=True)
        )
        await session.commit()

# ❌ Удалить промпт
async def delete_prompt(prompt_id: int, user_id: int):
    async with AsyncSessionLocal() as session:
        await session.execute(delete(Prompt).where(Prompt.id == prompt_id, Prompt.user_id == user_id))
        await session.commit()

# ✍️ Сохранение нового промпта (старый станет неактивным)
async def set_active_prompt(session: AsyncSession, user_id: int, text: str):
    await session.execute(
        update(Prompt).where(Prompt.user_id == user_id, Prompt.is_active == True).values(is_active=False)
    )
    session.add(Prompt(user_id=user_id, text=text, is_active=True))
    await session.commit()

# 💬 Добавить сообщение
async def add_message(session: AsyncSession, user_id: int, role: str, content: str):
    session.add(Message(user_id=user_id, role=role, content=content))
    await session.commit()

# 🧠 Получить последние сообщения
async def get_last_messages(session: AsyncSession, user_id: int, limit: int = 10):
    result = await session.execute(
        select(Message).where(Message.user_id == user_id).order_by(Message.id.desc()).limit(limit)
    )
    return list(reversed(result.scalars().all()))

# 🧼 Очистка истории сообщений
async def delete_user_messages(user_id: int, session: AsyncSession):
    await session.execute(delete(Message).where(Message.user_id == user_id))
    await session.commit()

# ⚙️ Память: включение/отключение
async def toggle_user_memory(user_id: int, session: AsyncSession) -> bool:
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        user = User(id=user_id)
        session.add(user)
        await session.commit()
        await session.refresh(user)
    user.use_memory = not user.use_memory
    await session.commit()
    return user.use_memory

async def get_user_memory_flag(user_id: int, session: AsyncSession) -> bool:
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    return user.use_memory if user else True

# 🖼 Temp посты
async def save_temp_post(session, user_id: int, file_id: str, caption: str, original: str) -> int:
    post = TempPost(user_id=user_id, file_id=file_id, caption=caption[:4000], original=original[:4000])
    session.add(post)
    await session.commit()
    await session.refresh(post)
    return post.id

async def get_temp_post(session, post_id: int) -> TempPost | None:
    return await session.get(TempPost, post_id)

async def update_temp_post_caption(session, post_id: int, new_caption: str):
    post = await session.get(TempPost, post_id)
    if post:
        post.caption = new_caption
        await session.commit()

async def delete_temp_post(session, post_id: int):
    post = await session.get(TempPost, post_id)
    if post:
        await session.delete(post)
        await session.commit()

# 🕓 Отложенные посты
async def get_user_scheduled_posts(session: AsyncSession, user_id: int):
    stmt = select(ScheduledPost).where(ScheduledPost.user_id == user_id, ScheduledPost.sent == False).order_by(ScheduledPost.scheduled_time)
    result = await session.execute(stmt)
    return result.scalars().all()

async def delete_scheduled_post(session: AsyncSession, post_id: int):
    post = await session.get(ScheduledPost, post_id)
    if post:
        await session.delete(post)
        await session.commit()
        return True
    return False

async def create_scheduled_post(user_id: int, channel_id: int, caption: str, file_id: str, scheduled_time):
    async with async_session() as session:
        post = ScheduledPost(
            user_id=user_id,
            channel_id=channel_id,
            caption=caption,
            file_id=file_id,
            scheduled_time=scheduled_time
        )
        session.add(post)
        await session.commit()

async def get_scheduled_posts_by_user(user_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(ScheduledPost).where(ScheduledPost.user_id == user_id).order_by(ScheduledPost.scheduled_time)
        )
        return result.scalars().all()

# 📝 Логирование
async def add_log(user_id: int, action_type: str, description: str = ""):
    async with get_async_session() as session:
        log = ActionLog(
            user_id=user_id,
            action_type=action_type,
            description=description,
            created_at=datetime.utcnow()
        )
        session.add(log)
        await session.commit()

async def get_last_logs(limit: int = 10):
    async with get_async_session() as session:
        result = await session.execute(
            select(ActionLog).options(joinedload(ActionLog.user)).order_by(desc(ActionLog.created_at)).limit(limit)
        )
        return result.scalars().all()

async def clear_logs():
    async with get_async_session() as session:
        await session.execute(delete(ActionLog))
        await session.commit()

# 👥 Пользователи и роли
async def get_all_users():
    async with get_async_session() as session:
        result = await session.execute(select(User))
        return result.scalars().all()

async def get_user_role(user_id: int) -> str:
    async with async_session() as session:
        result = await session.execute(select(User.role).where(User.id == user_id))
        return result.scalar_one_or_none() or "user"

async def is_superadmin(user_id: int) -> bool:
    return await get_user_role(user_id) == "superadmin"

async def is_admin(user_id: int) -> bool:
    return await get_user_role(user_id) in ["admin", "superadmin"]

async def get_user_by_id(user_id: int):
    async with get_async_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

async def set_user_role(user_id: int, role: str):
    async with get_async_session() as session:
        await session.execute(update(User).where(User.id == user_id).values(role=role))
        await session.commit()

async def delete_user(user_id: int):
    async with get_async_session() as session:
        await session.execute(delete(User).where(User.id == user_id))
        await session.commit()
