from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from bot.states.post_states import TextPostState, EditTextPost  # создадим эти стейты
from bot.services.openai_service import generate_text
from bot.keyboards.generate_text_keyboard import generate_text_action_keyboard
from aiogram import Router, types, F
from aiogram.filters import Command
router = Router()

# Шаг 1: команда для старта генерации текста

@router.message(Command(commands=['generate', 'generate_text']))
async def cmd_generate_text(message: types.Message, state: FSMContext):
    await message.answer("🖋 Введите тему или ключевые слова для генерации текста:")
    await state.set_state(TextPostState.waiting_for_prompt)

# Шаг 2: получаем промпт и дергаем OpenAI
@router.message(TextPostState.waiting_for_prompt)
async def handle_text_prompt(message: types.Message, state: FSMContext):
    prompt = message.text
    generated = await generate_text(prompt)
    # сохраняем в FSM data
    await state.update_data(prompt=prompt, generated=generated)
    kb = generate_text_action_keyboard()
    await message.answer(f"📝 Сгенерированный текст:\n\n{generated}", reply_markup=kb)
    await state.set_state(TextPostState.confirming)

# Шаг 3: обработчики inline-кнопок ("Ещё", "Редактировать", "Подтвердить")
# — regen
@router.callback_query(TextPostState.confirming, F.data == "regen_text")
async def cb_regen_text(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    prompt = data['prompt']
    new_text = await generate_text(prompt)
    await state.update_data(generated=new_text)
    kb = generate_text_action_keyboard()
    await callback.message.edit_text(f"📝 Новый текст:\n\n{new_text}", reply_markup=kb)
    await callback.answer()

# — edit
@router.callback_query(TextPostState.confirming, F.data == "edit_text")
async def cb_edit_text(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("✏️ Введите финальный вариант текста:")
    await state.set_state(EditTextPost.waiting_for_new_text)
    await callback.answer()

@router.message(EditTextPost.waiting_for_new_text)
async def handle_new_text(message: types.Message, state: FSMContext):
    new = message.text
    await state.update_data(generated=new)
    kb = generate_text_action_keyboard()
    await message.answer(f"✅ Текст обновлён:\n\n{new}", reply_markup=kb)
    await state.set_state(TextPostState.confirming)

# — confirm
@router.callback_query(TextPostState.confirming, F.data == "confirm_text_publish")
async def cb_confirm_text(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    final_text = data['generated']
    # тут вставь логику публикации (например, отправка в канал)
    await callback.message.answer(f"📣 Публикую:\n\n{final_text}")
    await state.clear()
    await callback.answer()
