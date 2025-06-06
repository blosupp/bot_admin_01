from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Awaitable, Dict, Any
from sqlalchemy import select
from database.db import async_session
from database.models import User

class RegisterCheckMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id

        async with async_session() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()

            # Если пользователя нет — показать список админов
            if not user:
                admins_result = await session.execute(
                    select(User.username).where(User.role.in_(["admin", "superadmin"]))
                )
                usernames = admins_result.scalars().all()
                admin_list = "\n".join([f"• @{u}" for u in usernames if u])

                await event.answer(
                    "❌ Вы не зарегистрированы в системе.\n\n"
                    "Напишите одному из админов:\n" + (admin_list or "🔒 Нет доступных админов.")
                )
                return

        return await handler(event, data)
