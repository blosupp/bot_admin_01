from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from database.crud import get_active_prompt, set_active_prompt, get_or_create_user
from database.db import get_async_session  # Не забудь про это!

router = Router()


# Состояния для изменения промпта
class PromptState(StatesGroup):
    waiting_for_prompt = State()


@router.message(Command("prompt"))
async def handle_prompt(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    await get_or_create_user(user_id, username)

    async with get_async_session() as session:
        current_prompt = await get_active_prompt(session, user_id)

    current_text = current_prompt.text if current_prompt else "❌ Нет активного промпта"

    await message.answer(
        f"🧠 Текущий промпт:\n\n<code>{current_text}</code>\n\n✏️ Введи новый промпт:",
        parse_mode="HTML"
    )
    await state.set_state(PromptState.waiting_for_prompt)


@router.message(PromptState.waiting_for_prompt)
async def save_prompt(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    new_prompt = message.text

    async with get_async_session() as session:
        await set_active_prompt(session, user_id, new_prompt)

    await message.answer("✅ Промпт сохранён!")
    await state.clear()
