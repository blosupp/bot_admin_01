from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.services.openai_service import generate_post_text
from database.crud import get_user_channels

router = Router()


class PostState(StatesGroup):
    choosing_channel = State()
    confirming_post = State()

# 📌 /post — генерация по промпту
@router.message(Command("post"))
async def start_post(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    channels = await get_user_channels(user_id)

    if not channels:
        await message.answer("📭 У тебя пока нет добавленных каналов.")
        return

    if len(channels) == 1:
        # Если канал один — сразу генерим
        await state.update_data(channel_id=channels[0].channel_id)
        text = await generate_post_text(user_id)
        await state.update_data(post_text=text)

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Опубликовать", callback_data="publish")],
            [InlineKeyboardButton(text="♻️ Сгенерировать снова", callback_data="regenerate")],
            [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_post")]
        ])

        await message.answer(
            f"<b>Предпросмотр:</b>\n\n{text}",
            parse_mode="HTML",
            reply_markup=keyboard
        )
        await state.set_state(PostState.confirming_post)
        return

    # Иначе — показать выбор каналов
    keyboard = [
        [InlineKeyboardButton(text=ch.title, callback_data=f"post_channel:{ch.channel_id}")]
        for ch in channels
    ]

    await message.answer(
        "Выбери канал для публикации поста:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    await state.set_state(PostState.choosing_channel)


# 📍 Пользователь выбрал канал — генерируем текст
@router.callback_query(F.data.startswith("post_channel:"))
async def generate_for_channel(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()  # обязательно, чтобы Telegram не выдал timeout

    user_id = callback.from_user.id
    channel_id = int(callback.data.split(":")[1])
    await state.update_data(channel_id=channel_id)

    text = await generate_post_text(user_id)
    await state.update_data(post_text=text)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Опубликовать", callback_data="publish")],
        [InlineKeyboardButton(text="♻️ Сгенерировать снова", callback_data="regenerate")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_post")]
    ])

    await callback.message.answer(
        f"<b>Предпросмотр:</b>\n\n{text}",
        parse_mode="HTML",
        reply_markup=keyboard
    )

    await state.set_state(PostState.confirming_post)


# 🔄 Сгенерировать новый текст
@router.callback_query(PostState.confirming_post, F.data == "regenerate")
async def regenerate_post(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    user_id = callback.from_user.id
    text = await generate_post_text(user_id)
    await state.update_data(post_text=text)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Опубликовать", callback_data="publish")],
        [InlineKeyboardButton(text="♻️ Сгенерировать снова", callback_data="regenerate")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_post")]
    ])

    await callback.message.edit_text(
        f"<b>Предпросмотр:</b>\n\n{text}",
        parse_mode="HTML",
        reply_markup=keyboard
    )


# ✅ Опубликовать
@router.callback_query(PostState.confirming_post, F.data == "publish")
async def publish_post(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()

    data = await state.get_data()
    channel_id = data.get("channel_id")
    post_text = data.get("post_text")

    if not post_text:
        await callback.message.edit_text("❌ Пост пустой. Попробуй снова.")
        await state.clear()
        return

    try:
        await bot.send_message(chat_id=channel_id, text=post_text)
        await callback.message.edit_text("✅ Пост опубликован!")
    except Exception as e:
        await callback.message.edit_text(
            f"❌ Ошибка при публикации:\n<code>{e}</code>",
            parse_mode="HTML"
        )

    await state.clear()


# ❌ Отмена
@router.callback_query(PostState.confirming_post, F.data == "cancel_post")
async def cancel_post(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.edit_text("❌ Публикация отменена.")
