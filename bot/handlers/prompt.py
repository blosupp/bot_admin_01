from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

router = Router()

user_prompts = {}

# Состояния для изменения промпта
class PromptState(StatesGroup):
    waiting_for_prompt = State()

@router.message(Command("prompt"))
async def handle_prompt(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    current = user_prompts.get(user_id, "📝 Промт по умолчанию...")
    await message.answer(f"Текущий промт:\n\n{current}\n\n✏️ Напиши новый промт:")
    await state.set_state(PromptState.waiting_for_prompt)

@router.message(PromptState.waiting_for_prompt)
async def save_prompt(message: types.Message, state: FSMContext):
    user_prompts[message.from_user.id] = message.text
    await message.answer("✅ Промт обновлён!")
    await state.clear()
