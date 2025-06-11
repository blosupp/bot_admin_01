from aiogram import Router, types
from aiogram.filters import Command
from database.crud import get_user_role
from database.db import async_session
from database.models import User
from sqlalchemy import select
from database.crud import get_or_create_user

router = Router()

@router.message(Command("me"))
async def show_my_profile(message: types.Message):
    user = await get_or_create_user(message.from_user)

    nickname = f"@{user.username}" if user.username else "(без ника)"

    text = (
        f"<b>👤 Ваш профиль:</b>\n\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"🔗 Ник: {nickname}\n"
        f"🎭 Роль: <b>{user.role}</b>\n"
        f"🧾 Постов: {user.post_count}\n"
        f"💰 Баланс: {user.balance}"
    )

    await message.answer(text, parse_mode="HTML")
