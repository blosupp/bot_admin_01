from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer(
        "🤖 <b>Доступные команды:</b>\n\n"
        "<b>📌 Основное:</b>\n"
        "/help — список всех команд\n"
        "/prompt — показать / изменить промпт\n"
        "/generate — сгенерировать пост на основе промпта\n\n"
        "<b>📡 Каналы:</b>\n"
        "/add_channel — добавить канал (перешли сообщение из канала)\n"
        "/my_channels — список твоих каналов\n\n"
        "<b>ℹ️ Важно:</b>\n"
        "• Бот может публиковать посты <b>только в каналы, где он добавлен как админ</b> с правом \"публиковать сообщения\".\n"
        "• После генерации поста ты можешь выбрать канал для публикации через кнопки.\n\n"
        "<b>🧠 Как пользоваться:</b>\n"
        "1. Установи промпт через /prompt\n"
        "2. Введи /generate\n"
        "3. Подтверди или сгенерируй ещё\n"
        "4. Выбери канал для публикации\n",
        parse_mode="HTML"
    )
