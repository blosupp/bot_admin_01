from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from database.crud import get_user_scheduled_posts, delete_scheduled_post

router = Router()

@router.message(Command("queue"))
async def show_scheduled_posts(message: Message, session: AsyncSession):
    posts = await get_user_scheduled_posts(session, user_id=message.from_user.id)

    if not posts:
        await message.answer("У вас нет отложенных публикаций.")
        return

    for post in posts:
        text = f"📅 <b>{post.scheduled_time:%d.%m %H:%M}</b>\n"
        text += f"📢 <i>Канал ID:</i> <code>{post.channel_id}</code>\n\n"

        if post.caption:
            text += post.caption[:100] + "..."
        else:
            text += "⚠️ Без текста."

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🗑 Отменить",
                        callback_data=f"cancel_post:{post.id}"
                    )
                ]
            ]
        )

        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
