# ✅ handlers/generate.py — обработка генерации, редактирования и публикации фото-постов с удалением

from aiogram import Router, types, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery

from bot.states.post_states import PostState, EditPhotoPost
from bot.services.openai_service import generate_text
from bot.keyboards.generate import generate_action_keyboard
from bot.config import OPENAI_API_KEY
from bot.states.post_states import SchedulePostState
from datetime import datetime
from database.models import ScheduledPost



from database.crud import (
    get_or_create_user,
    get_active_prompt,
    get_temp_post,
    get_user_channels,
    save_temp_post,
    update_temp_post_caption,
    delete_temp_post  # ✅ новый импорт
)
from database.db import get_async_session

from openai import AsyncOpenAI

router = Router()
client = AsyncOpenAI(api_key=OPENAI_API_KEY)
user_generations = {}

# 📌 /generate — генерация текстового поста по активному промпту
@router.message(F.text.lower() == "/generate")
async def generate_post(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username or "unknown"
    await get_or_create_user(user_id, username)

    async with get_async_session() as session:
        prompt = await get_active_prompt(session, user_id)
        if not prompt:
            await message.answer("❌ У тебя пока нет активного промпта. Введи /prompt, чтобы задать его.")
            return
    try:
        response = await client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": "Сгенерируй пост по описанию."}
            ],
            temperature=0.7,
            max_tokens=500
        )
        text = response.choices[0].message.content
        user_generations[user_id] = text
        await message.answer(text, reply_markup=generate_action_keyboard())

    except Exception as e:
        await message.answer(f"\u274c Ошибка при генерации:\n\n{e}")


# 📷 Обработка присланного фото с подписью и генерация текста
@router.message(F.photo)
async def handle_photo_with_caption(message: Message):
    caption = message.caption
    if not caption:
        await message.answer("\u2753 Добавь подпись к фото.")
        return

    await message.answer("\u270d Генерирую пост...")
    generated_text = await generate_text(caption)
    safe_caption = generated_text[:1024]
    file_id = message.photo[-1].file_id

    async with get_async_session() as session:
        temp_id = await save_temp_post(session, message.from_user.id, file_id, generated_text, caption)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Опубликовать", callback_data=f"publish_temp:{temp_id}")],
        [InlineKeyboardButton(text="✏ Редактировать", callback_data=f"edit_temp:{temp_id}")],
        [InlineKeyboardButton(text="♻ Сгенерировать заново", callback_data=f"regen_temp:{temp_id}")],
        [InlineKeyboardButton(text="⏰ Отложить", callback_data=f"schedule_temp:{temp_id}")],
        [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_temp:{temp_id}")]
    ])

    await message.answer_photo(photo=file_id, caption=safe_caption, reply_markup=kb)


# ✏️ Обработка редактирования текста поста
@router.callback_query(F.data.startswith("edit_temp:"))
async def edit_temp_post(callback: CallbackQuery, state: FSMContext):
    temp_id = int(callback.data.split(":")[1])
    async with get_async_session() as session:
        post = await get_temp_post(session, temp_id)

    await state.set_state(EditPhotoPost.waiting_for_new_text)
    await state.update_data(temp_id=temp_id)
    await callback.message.answer(f"\U0001f4dd Текущий текст:\n\n{post.caption}\n\n✏ Введи новый:")


# 💾 Сохраняем новый текст после редактирования
@router.message(EditPhotoPost.waiting_for_new_text)
async def handle_new_caption(message: Message, state: FSMContext):
    data = await state.get_data()
    temp_id = data.get("temp_id")
    new_text = message.text
    async with get_async_session() as session:
        await update_temp_post_caption(session, temp_id, new_text)
    await message.answer("\u2705 Обновлено. Нажми «Опубликовать» для отправки.")
    await state.clear()


# ♻ Повторная генерация по исходной подписи
@router.callback_query(F.data.startswith("regen_temp:"))
async def regenerate_caption(callback: CallbackQuery):
    temp_id = int(callback.data.split(":")[1])
    async with get_async_session() as session:
        post = await get_temp_post(session, temp_id)
        if not post:
            await callback.message.answer("\u274c Пост не найден.")
            return
        new_caption = await generate_text(post.original)
        post.caption = new_caption
        await session.commit()
    await callback.message.answer("\u267b Пост сгенерирован заново. Можешь опубликовать или изменить.")


# 📂 Удаление поста (из чата и из базы)
@router.callback_query(F.data.startswith("delete_temp:"))
async def delete_temp(callback: CallbackQuery):
    temp_id = int(callback.data.split(":")[1])
    async with get_async_session() as session:
        await delete_temp_post(session, temp_id)
    try:
        await callback.message.delete()
    except Exception:
        await callback.message.answer("✅ Пост удалён, но не удалось удалить сообщение.")


# ✅ Опубликовать — обработка в зависимости от количества каналов
@router.callback_query(F.data.startswith("publish_temp:"))
async def choose_channel_or_publish(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    temp_id = int(callback.data.split(":")[1])
    user_id = callback.from_user.id

    async with get_async_session() as session:
        post = await get_temp_post(session, temp_id)
        channels = await get_user_channels(user_id)

    if not post or not channels:
        await callback.message.answer("\u274c Пост не найден или нет добавленных каналов.")
        return

    await state.update_data(file_id=post.file_id, post_text=post.caption, temp_post_id=temp_id)

    if len(channels) == 1:
        await state.update_data(channel_id=channels[0].channel_id)
        await publish_post_to_channel(callback, state, bot)
        return

    keyboard = [
        [InlineKeyboardButton(text=ch.title, callback_data=f"photo_channel:{ch.channel_id}")]
        for ch in channels
    ]
    await callback.message.answer(
        "Выбери канал для публикации:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    await state.set_state(PostState.choosing_channel)


# 📂 Выбор канала — сохраняем и показываем предпросмотр
@router.callback_query(F.data.startswith("photo_channel:"))
async def photo_choose_channel(callback: CallbackQuery, state: FSMContext):
    channel_id = int(callback.data.split(":")[1])
    await callback.answer()
    await state.update_data(channel_id=channel_id)
    data = await state.get_data()

    file_id = data.get("file_id")
    post_text = data.get("post_text")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="\u2705 Опубликовать", callback_data="confirm_photo_publish")],
        [InlineKeyboardButton(text="\u274c Отменить", callback_data="cancel_post")]
    ])
    await callback.message.answer_photo(photo=file_id, caption=post_text[:1024], reply_markup=keyboard)
    await state.set_state(PostState.confirming_post)


# 📢 Публикация в выбранный канал (финальный шаг) с автоудалением TempPost
@router.callback_query(PostState.confirming_post, F.data == "confirm_photo_publish")
async def publish_post_to_channel(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    data = await state.get_data()

    channel_id = data.get("channel_id")
    post_text = data.get("post_text")
    file_id = data.get("file_id")
    temp_post_id = data.get("temp_post_id")

    try:
        await bot.send_photo(chat_id=channel_id, photo=file_id, caption=post_text[:1024])
        await callback.message.answer("\u2705 Фото-пост опубликован!")

        # ❌ Автоудаление записи из TempPost
        async with get_async_session() as session:
            await delete_temp_post(session, temp_post_id)

    except Exception as e:
        await callback.message.answer(f"\u274c Ошибка:\n<code>{e}</code>", parse_mode="HTML")

    await state.clear()

@router.callback_query(F.data.startswith("schedule_temp:"))
async def ask_for_datetime(callback: CallbackQuery, state: FSMContext):
    """
    ⏰ Хэндлер по нажатию на кнопку «Отложить»
    """
    temp_id = int(callback.data.split(":")[1])

    await state.update_data(temp_post_id=temp_id)
    await state.set_state(SchedulePostState.choosing_datetime)

    await callback.message.answer(
        "📅 Введи дату и время публикации в формате:\n\n<code>ДД.ММ.ГГГГ ЧЧ:ММ</code>",
        parse_mode="HTML"
    )

@router.message(SchedulePostState.choosing_datetime)
async def handle_datetime_input(message: Message, state: FSMContext):
    """
    ⌚ Принимает дату и время от пользователя в формате 'ДД.ММ.ГГГГ ЧЧ:ММ'
    """
    user_input = message.text.strip()

    try:
        # ⏱ Пробуем распарсить введённую строку в datetime-объект
        scheduled_dt = datetime.strptime(user_input, "%d.%m.%Y %H:%M")

        # ✅ Сохраняем дату и время во временное состояние FSM
        await state.update_data(scheduled_time=scheduled_dt)

        await message.answer(
            f"🗓 Публикация будет запланирована на: <b>{scheduled_dt.strftime('%d.%m.%Y %H:%M')}</b>\n\nНажми «Подтвердить», чтобы сохранить.",
            parse_mode="HTML"
        )
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_schedule")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_post")]
        ])
        await message.answer("Подтверди публикацию или отмени:", reply_markup=keyboard)
        # ⏭ Переход к следующему состоянию
        await state.set_state(SchedulePostState.confirming)

    except ValueError:
        await message.answer("❌ Неверный формат. Введи дату и время так:\n\n<code>ДД.ММ.ГГГГ ЧЧ:ММ</code>", parse_mode="HTML")


@router.callback_query(SchedulePostState.confirming, F.data == "confirm_schedule")
async def confirm_scheduled_post(callback: CallbackQuery, state: FSMContext):
    """
    ✅ Сохраняет пост в таблицу scheduled_posts
    """
    await callback.answer()

    data = await state.get_data()

    async with get_async_session() as session:
        scheduled = ScheduledPost(
            user_id=callback.from_user.id,
            channel_id=data["channel_id"],
            caption=data["post_text"],
            file_id=data["file_id"],
            scheduled_time=data["scheduled_time"]
        )
        session.add(scheduled)
        await session.commit()

    await callback.message.answer("✅ Пост отложен! Он будет опубликован в указанное время.")
    await state.clear()
