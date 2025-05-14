from aiogram import Router, types, F
from aiogram.filters import Command
from bot.services.openai_service import generate_text
from bot.keyboards.generate import generate_action_keyboard, generate_publish_keyboard
from bot.handlers.prompt import user_prompts
from bot.config import TEST_CHANNEL_ID
from bot.handlers.channels import user_channels
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import  StatesGroup, State

class PostState(StatesGroup):
    waiting_for_edit = State()

router = Router()

# Хранилище последних генераций
user_generations = {}


@router.message(Command("generate"))
async def handle_generate(message: types.Message):
    user_id = message.from_user.id
    prompt = user_prompts.get(user_id, "Сгенерируй пример поста.")
    await message.answer("✍️ Генерирую текст...")

    result = await generate_text(prompt)
    user_generations[user_id] = result

    await message.answer(result, reply_markup=generate_action_keyboard())


@router.callback_query(F.data.in_(["regenerate", "confirm", "cancel"]))
async def handle_generate_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    action = callback.data

    if action == "regenerate":
        prompt = user_prompts.get(user_id, "Сгенерируй новый пост.")
        new_result = await generate_text(prompt)
        user_generations[user_id] = new_result

        try:
            await callback.answer("🔁 Сгенерировано заново")
        except:
            pass

        await callback.message.edit_text(new_result, reply_markup=generate_action_keyboard())


    elif action == "confirm":
        channels = user_channels.get(user_id)
        if not channels:
            await callback.answer("❗ У тебя нет сохранённых каналов")
            return
        await callback.message.edit_reply_markup(reply_markup=generate_publish_keyboard(channels))
        try:
            await callback.answer("📋 Выбери канал для публикации")
        except:
            pass
    elif action == "cancel":
        user_generations.pop(user_id, None)
        try:
            await callback.answer("❌ Отменено")
        except:
            pass
        await callback.message.edit_reply_markup(reply_markup=None)


@router.callback_query(F.data.startswith("publish:"))
async def publish_to_channel(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    channel_id = int(callback.data.split(":")[1])
    text = user_generations.get(user_id)

    if not text:
        await callback.answer("❌ Нечего публиковать")
        return

    try:
        await callback.bot.send_message(channel_id, text)
        await callback.answer("✅ Пост отправлен!")
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {e}")

    await callback.message.edit_reply_markup(reply_markup=None)


@router.callback_query(F.data == "edit")
async def handle_edit_request(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("✏️ Введи новый текст поста:")
    await state.set_state(PostState.waiting_for_edit)


@router.message(PostState.waiting_for_edit)
async def receive_edited_text(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_generations[user_id] = message.text  # заменяем текст
    await message.answer("✅ Пост обновлён. Выбери канал для публикации:")

    from bot.handlers.channels import user_channels
    channels = user_channels.get(user_id, [])

    if channels:
        from bot.keyboards.generate import generate_publish_keyboard
        await message.answer(message.text, reply_markup=generate_publish_keyboard(channels))
    else:
        await message.answer("❗ У тебя нет добавленных каналов.")

    await state.clear()
