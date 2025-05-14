from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from database.crud import get_active_prompt, set_active_prompt, get_or_create_user



router = Router()


# Состояния для изменения промпта
class PromptState(StatesGroup):
    waiting_for_prompt = State()

@router.message(Command("prompt"))
async def handle_prompt(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    await get_or_create_user(user_id, username)

    current = await get_active_prompt(user_id)
    await message.answer(
        f"🧠 Текущий промпт:\n\n<code>{current}</code>\n\n✏️ Введи новый промпт:",
        parse_mode="HTML"
    )
    await state.set_state(PromptState.waiting_for_prompt)

@router.message(PromptState.waiting_for_prompt)
async def save_prompt(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await set_active_prompt(user_id, message.text)
    await message.answer("✅ Промпт сохранён!")
    await state.clear()