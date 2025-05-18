from aiogram import Router, types, F
from bot.services.openai_service import generate_text
from bot.services.openai_service import generate_text_with_memory

from database.db import get_async_session
from database.crud import add_message

router = Router()

@router.message(F.text & ~F.text.startswith("/"))
async def gpt_dialogue(message: types.Message):
    user_id = message.from_user.id
    user_input = message.text

    reply = await generate_text_with_memory(user_id, user_input)
    await message.answer(reply)

    # 🔧 временный тест
    async with get_async_session() as session:
        await add_message(session, user_id, "user", user_input)
        await add_message(session, user_id, "assistant", reply)
