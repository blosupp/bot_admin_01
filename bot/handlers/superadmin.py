from aiogram import Router, types
from aiogram.filters import Command
from database.crud import is_superadmin
from database.db import async_session
from database.models import ActionLog
from sqlalchemy import select, desc
from sqlalchemy import update
from database.crud import add_log
from database.models import User
from database.crud import get_user_role
from sqlalchemy import delete
from database.models import ScheduledPost
from aiogram.types import Message


from database.models import User

from database.crud import is_admin, is_superadmin


router = Router()

@router.message(Command("logs"))
async def view_logs(message: types.Message):
    user_id = message.from_user.id
    args = message.text.strip().split()

    if not await is_superadmin(user_id):
        await message.answer("🚫 Доступ запрещён. Только для суперадмина.")
        return

    # Опциональный фильтр: /logs [тип]
    log_type = args[1] if len(args) > 1 else None

    async with async_session() as session:
        query = select(ActionLog).order_by(desc(ActionLog.created_at)).limit(30)

        if log_type:
            query = query.where(ActionLog.action_type == log_type)

        result = await session.execute(query)
        logs = result.scalars().all()

        if not logs:
            await message.answer("📭 Логи пусты.")
            return

        text = f"<b>📋 Последние действия{' (' + log_type + ')' if log_type else ''}:</b>\n\n"

        for log in logs:
            if not log or not log.user_id:
                continue

            try:
                user_result = await session.execute(
                    select(User).where(User.id == log.user_id)
                )
                user = user_result.scalar_one_or_none()
                username = f"@{user.username}" if user and user.username else "(ник неизвестен)"
            except Exception:
                username = "(ошибка получения ника)"

            text += (
                f"🕒 {log.created_at.strftime('%d.%m.%Y %H:%M')} | "
                f"{username} <code>{log.user_id}</code>\n"
                f"<b>{log.action_type}</b>: {log.description}\n\n"
            )

    await message.answer(text, parse_mode="HTML")


@router.message(Command("add_admin"))
async def add_admin(message: types.Message):
    user_id = message.from_user.id
    if not await is_superadmin(user_id):
        await message.answer("🚫 Только суперадмин может добавлять админов.")
        return

    args = message.text.strip().split()
    if len(args) != 2 or not args[1].isdigit():
        await message.answer("⚠️ Использование: /add_admin <user_id>")
        return

    target_id = int(args[1])
    async with async_session() as session:
        await session.execute(update(User).where(User.id == target_id).values(role="admin"))
        await session.commit()

    await add_log(user_id, "role_change", f"Назначен админ: {target_id}")
    await message.answer(f"✅ Пользователь {target_id} теперь админ.")


@router.message(Command("remove_admin"))
async def remove_admin(message: types.Message):
    user_id = message.from_user.id
    if not await is_superadmin(user_id):
        await message.answer("🚫 Только суперадмин может снимать админов.")
        return

    args = message.text.strip().split()
    if len(args) != 2 or not args[1].isdigit():
        await message.answer("⚠️ Использование: /remove_admin <user_id>")
        return

    target_id = int(args[1])
    async with async_session() as session:
        await session.execute(update(User).where(User.id == target_id).values(role="user"))
        await session.commit()

    await add_log(user_id, "role_change", f"Снят админ: {target_id}")
    await message.answer(f"☑️ Пользователь {target_id} теперь обычный юзер.")





@router.message(Command("add_user"))
async def add_user(message: types.Message):
    sender_id = message.from_user.id
    args = message.text.strip().split()

    if not await is_admin(sender_id):
        await message.answer("🚫 Недостаточно прав.")
        return

    if len(args) != 2 or not args[1].isdigit():
        await message.answer("⚠️ Использование: /add_user <user_id>")
        return

    new_user_id = int(args[1])
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == new_user_id))
        if result.scalar_one_or_none():
            await message.answer("⚠️ Пользователь уже существует.")
            return
        user = User(id=new_user_id, role="client")
        session.add(user)
        await session.commit()

    await add_log(sender_id, "user_add", f"Добавлен пользователь {new_user_id}")
    await message.answer(f"✅ Пользователь {new_user_id} добавлен.")


@router.message(Command("remove_user"))
async def remove_user(message: types.Message):
    sender_id = message.from_user.id
    args = message.text.strip().split()

    if not await is_admin(sender_id):
        await message.answer("🚫 Недостаточно прав.")
        return

    if len(args) != 2 or not args[1].isdigit():
        await message.answer("⚠️ Использование: /remove_user <user_id>")
        return

    target_id = int(args[1])
    target_role = await get_user_role(target_id)

    # ⚠️ Админ не может удалить админа или суперадмина
    if target_role in ["admin", "superadmin"] and not await is_superadmin(sender_id):
        await message.answer("🚫 Нельзя удалить администратора.")
        return

    async with async_session() as session:
        await session.execute(delete(User).where(User.id == target_id))
        await session.commit()

    await add_log(sender_id, "user_remove", f"Удалён пользователь {target_id}")
    await message.answer(f"🗑 Пользователь {target_id} удалён.")




@router.message(Command("users"))
async def list_users(message: types.Message):
    sender_id = message.from_user.id

    if not await is_admin(sender_id):
        await message.answer("🚫 Недостаточно прав.")
        return

    async with async_session() as session:
        result = await session.execute(select(User).order_by(User.role, User.id))
        users = result.scalars().all()

    if not users:
        await message.answer("📭 Пользователи не найдены.")
        return

    text = "<b>📋 Список пользователей:</b>\n\n"
    for user in users:
        nickname = f"@{user.username}" if user.username else "(без ника)"
        text += f"👤 <code>{user.id}</code> — {nickname} — <b>{user.role}</b>\n"

    await message.answer(text, parse_mode="HTML")



@router.message(Command("admins"))
async def list_admins(message: types.Message):
    sender_id = message.from_user.id

    if not await is_superadmin(sender_id):
        await message.answer("🚫 Только для суперадмина.")
        return

    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.role == "admin")
        )
        admins = result.scalars().all()

    if not admins:
        await message.answer("📭 Админы не найдены.")
        return

    text = "<b>👥 Список админов:</b>\n\n"
    for admin in admins:
        username = f"@{admin.username}" if admin.username else "(без ника)"
        text += f"🔧 {username} — <code>{admin.id}</code>\n"

    await message.answer(text, parse_mode="HTML")

@router.message(Command("clear_logs"))
async def clear_logs(message: types.Message):
    if not await is_superadmin(message.from_user.id):
        await message.answer("🚫 Недостаточно прав.")
        return

    async with async_session() as session:
        await session.execute(delete(ActionLog))
        await session.commit()

    await message.answer("🧹 Все логи успешно удалены.")



@router.message(Command("stats"))
async def show_stats(message: types.Message):
    user_id = message.from_user.id

    if not await is_admin(user_id):
        await message.answer("🚫 Доступ только для админов.")
        return

    is_super = await is_superadmin(user_id)

    async with async_session() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()

        post_result = await session.execute(select(ScheduledPost))
        posts = post_result.scalars().all()

        post_map = {}
        for post in posts:
            post_map[post.user_id] = post_map.get(post.user_id, 0) + 1

        log_result = await session.execute(
            select(ActionLog).order_by(desc(ActionLog.created_at)).limit(1)
        )
        last_log = log_result.scalar_one_or_none()

    text = "<b>📊 Статистика по пользователям:</b>\n\n"

    for user in users:
        if not is_super and user.role == "superadmin":
            continue

        username = f"@{user.username}" if user.username else f"ID: {user.id}"
        post_count = post_map.get(user.id, 0)
        text += f"{username} — <i>{user.role}</i> — 🧾 {post_count} постов\n"

    if last_log:
        name = f"@{last_log.user.username}" if last_log.user and last_log.user.username else f"ID: {last_log.user_id}"
        text += (
            f"\n🕒 Последнее действие:\n"
            f"{name} — <i>{last_log.action_type}</i>\n"
            f"{last_log.description}"
        )

    await message.answer(text, parse_mode="HTML")


@router.message(Command("set_balance"))
async def set_balance(message: Message):
    if not await is_superadmin(message.from_user.id):
        return await message.answer("🚫 Только для суперадмина")

    args = message.text.split()
    if len(args) != 3:
        return await message.answer("⚠️ Использование: /set_balance @username 100")

    username = args[1].lstrip("@")
    try:
        amount = int(args[2])
    except ValueError:
        return await message.answer("❌ Неверное значение баланса")

    async with async_session() as session:
        result = await session.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
        if not user:
            return await message.answer("❌ Пользователь не найден")

        await session.execute(update(User).where(User.id == user.id).values(balance=amount))
        await session.commit()
        await message.answer(f"✅ Баланс пользователя @{username} установлен: {amount}")




@router.message(Command("add_balance"))
async def add_balance(message: Message):
    if not await is_superadmin(message.from_user.id):
        return await message.answer("🚫 Только для суперадмина")

    args = message.text.split()
    if len(args) != 3:
        return await message.answer("⚠️ Использование: /add_balance @username 10")

    username = args[1].lstrip("@")
    try:
        amount = int(args[2])
    except ValueError:
        return await message.answer("❌ Неверное значение")

    async with async_session() as session:
        result = await session.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
        if not user:
            return await message.answer("❌ Пользователь не найден")

        new_balance = user.balance + amount
        await session.execute(update(User).where(User.id == user.id).values(balance=new_balance))
        await session.commit()
        await message.answer(f"💰 Баланс @{username} увеличен до {new_balance}")
