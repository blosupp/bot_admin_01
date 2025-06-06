from aiogram import Router, types, F
from bot.services.openai_service import generate_text
from bot.services.openai_service import generate_text_with_memory
from aiogram.filters import Command
from aiogram.types import Message


from database.crud import add_message
from database.crud import delete_user_messages
from database.db import get_async_session
from database.crud import toggle_user_memory


router = Router()

@router.message(F.text & ~F.text.startswith("/"))
async def gpt_dialogue(message: types.Message):
    user_id = message.from_user.id
    user_input = message.text

    reply = await generate_text_with_memory(user_id, user_input)
    await message.answer(reply)

    ## 🔧 временный тест
    #async with get_async_session() as session:
    #    await add_message(session, user_id, "user", user_input)
    #    await add_message(session, user_id, "assistant", reply)


@router.message(Command("forget"))
async def forget_memory(message: Message):
    """
    Команда /forget:
    ⏳ Удаляет всю историю сообщений пользователя из памяти GPT
    """
    user_id = message.from_user.id

    async with get_async_session() as session:  # 🔄 открываем сессию с БД
        await delete_user_messages(user_id, session)  # 🧹 удаляем сообщения

    await message.answer("🧠 История очищена. Начнем с чистого листа!")



@router.message(Command("chatmode"))
async def toggle_chatmode(message: Message):
    """
    Команда /chatmode:
    🔁 Переключает память GPT (вкл/выкл)
    """
    user_id = message.from_user.id

    async with get_async_session() as session:
        new_mode = await toggle_user_memory(user_id, session)

    mode_text = "🧠 Память включена.\nGPT будет помнить контекст." if new_mode else "💤 Память отключена.\nGPT не будет помнить прошлые сообщения."
    await message.answer(f"{mode_text}\n\nПовторно введите /chatmode для переключения.")