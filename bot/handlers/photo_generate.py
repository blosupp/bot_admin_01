from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram import Bot
from datetime import datetime

from bot.states.post_states import PhotoPostState, EditPhotoPost, SchedulePostState
from bot.services.openai_service import generate_text
from bot.keyboards.generate_photo_keyboard import (
    generate_photo_action_keyboard,
    generate_photo_publish_keyboard,
    generate_photo_schedule_keyboard
)
from database.crud import (
    save_temp_post,
    get_temp_post,
    update_temp_post_caption,
    delete_temp_post,
    get_user_channels
)
from database.db import get_async_session
from database.models import ScheduledPost

router = Router()


@router.message(F.photo)
async def handle_photo_with_caption(message: Message, state: FSMContext):
    caption = message.caption or ""
    if not caption:
        await message.answer("❓ Добавь текстовый подпись к фото.")
        return

    await message.answer("✍️ Генерирую пост…")
    generated = await generate_text(caption)
    safe_caption = generated[:1024]
    file_id = message.photo[-1].file_id

    async with get_async_session() as session:
        temp_id = await save_temp_post(session, message.from_user.id, file_id, generated, caption)

    await state.update_data(
        file_id=file_id,
        post_text=generated,
        temp_post_id=temp_id
    )


    # клавиатура действий
    kb = generate_photo_action_keyboard(temp_id)
    await message.answer_photo(photo=file_id, caption=safe_caption, reply_markup=kb)
    await state.set_state(PhotoPostState.confirming_post)


@router.callback_query(PhotoPostState.confirming_post, F.data.startswith("regen_temp:"))
async def cb_regen_caption(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    temp_id = int(callback.data.split(":")[1])

    async with get_async_session() as session:
        post = await get_temp_post(session, temp_id)
        if not post:
            await callback.message.answer("❌ Пост не найден.")
            return
        new_caption = await generate_text(post.original)
        post.caption = new_caption
        await session.commit()

    kb = generate_photo_action_keyboard(temp_id)
    # обновляем подпись под уже отправленным фото
    await callback.message.edit_caption(caption=new_caption[:1024], reply_markup=kb)
    await state.set_state(PhotoPostState.confirming_post)


@router.callback_query(PhotoPostState.confirming_post, F.data.startswith("edit_temp:"))
async def cb_edit_caption(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    temp_id = int(callback.data.split(":")[1])

    async with get_async_session() as session:
        post = await get_temp_post(session, temp_id)
    await state.update_data(temp_id=temp_id)
    await state.set_state(EditPhotoPost.waiting_for_new_text)

    await callback.message.answer(f"✏️ Текущая подпись:\n\n{post.caption}\n\nВведите новую:")


@router.message(EditPhotoPost.waiting_for_new_text)
async def handle_new_caption(message: Message, state: FSMContext):
    data = await state.get_data()
    temp_id = data.get("temp_id")
    new_text = message.text

    async with get_async_session() as session:
        await update_temp_post_caption(session, temp_id, new_text)

    kb = generate_photo_action_keyboard(temp_id)
    await message.answer("✅ Подпись обновлена.", reply_markup=kb)
    await state.set_state(PhotoPostState.confirming_post)


@router.callback_query(PhotoPostState.confirming_post, F.data == "confirm_photo_publish")
async def cb_confirm_publish(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()

    data = await state.get_data()
    file_id = data.get("file_id")
    caption = data.get("post_text")
    temp_id = data.get("temp_post_id")

    # на всякий случай:
    if not file_id or not caption or not temp_id:
        await callback.message.answer("❌ Что-то пошло не так, начни заново.")
        await state.clear()
        return

    # получаем список каналов
    channels = await get_user_channels(callback.from_user.id)
    if not channels:
        await callback.message.answer("📭 У тебя нет сохранённых каналов.")
        await state.clear()
        return

    # если канал один — сразу публикуем
    if len(channels) == 1:
        channel_id = channels[0].channel_id
        await bot.send_photo(chat_id=channel_id, photo=file_id, caption=caption[:1024])
        # удаляем temp-запись
        async with get_async_session() as session:
            await delete_temp_post(session, temp_id)
        await callback.message.answer("✅ Фото-пост опубликован!")
        await state.clear()
    else:
        # несколько каналов — выбираем
        choices = [(ch.channel_id, ch.title) for ch in channels]
        kb = generate_photo_publish_keyboard(choices)
        await callback.message.answer("Выберите канал для публикации:", reply_markup=kb)
        await state.set_state(PhotoPostState.choosing_channel)


@router.callback_query(PhotoPostState.choosing_channel, F.data.startswith("photo_channel:"))
async def cb_photo_choose_channel(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    channel_id = int(callback.data.split(":")[1])
    await state.update_data(channel_id=channel_id)

    data = await state.get_data()
    file_id = data.get("file_id")
    caption = data.get("post_text")
    temp_id = data.get("temp_post_id")

    # публикуем
    await bot.send_photo(chat_id=channel_id, photo=file_id, caption=caption[:1024])
    # удаляем TempPost
    async with get_async_session() as session:
        await delete_temp_post(session, temp_id)

    await callback.message.answer("✅ Фото-пост опубликован!")
    await state.clear()


@router.callback_query(PhotoPostState.confirming_post, F.data.startswith("schedule_temp:"))
async def cb_schedule_temp(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    temp_id = int(callback.data.split(":")[1])
    await state.update_data(temp_post_id=temp_id)
    await state.set_state(SchedulePostState.choosing_datetime)

    await callback.message.answer(
        "📅 Введите дату и время в формате <code>ДД.MM.ГГГГ ЧЧ:ММ</code>",
        parse_mode="HTML",
        reply_markup=generate_photo_schedule_keyboard()
    )


@router.message(SchedulePostState.choosing_datetime)
async def handle_datetime_input(message: Message, state: FSMContext):
    user_input = message.text.strip()
    try:
        sched_dt = datetime.strptime(user_input, "%d.%m.%Y %H:%M")
        await state.update_data(scheduled_time=sched_dt)

        await message.answer(
            f"🗓 Пост запланирован на <b>{sched_dt.strftime('%d.%m.%Y %H:%M')}</b>.\nНажмите «Подтвердить» или «Отмена».",
            parse_mode="HTML",
            reply_markup=generate_photo_schedule_keyboard()
        )
        await state.set_state(SchedulePostState.confirming)
    except ValueError:
        await message.answer("❌ Неверный формат. Попробуйте ещё раз:\n<code>ДД.MM.ГГГГ ЧЧ:ММ</code>", parse_mode="HTML")


@router.callback_query(SchedulePostState.confirming, F.data == "confirm_schedule")
async def cb_confirm_schedule(callback: CallbackQuery, state: FSMContext):
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
        # удаляем временный пост
        await delete_temp_post(session, data["temp_post_id"])

    await callback.message.answer("✅ Фото-пост отложен!")
    await state.clear()


@router.callback_query(PhotoPostState.confirming_post, F.data == "cancel_post")
async def cb_cancel(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    try:
        await callback.message.delete()
    except:
        pass



# Отмена в основном фото-флоу (когда показываются 🔁 Ещё, ✏️ Редактировать, ✅ Подтвердить, ❌ Отмена)
@router.callback_query(PhotoPostState.confirming_post, F.data == "cancel_post")
async def cb_cancel_photo(callback: CallbackQuery, state: FSMContext):
    await callback.answer("❌ Отменено", show_alert=False)
    # удаляем сообщение-карусель с фото и кнопками
    try:
        await callback.message.delete()
    except:
        pass
    await state.clear()

# Отмена в режиме отложенной публикации (⏰ Запланировать → ввод даты → «Подтвердить»/«❌ Отмена»)
@router.callback_query(SchedulePostState.confirming, F.data == "cancel_post")
async def cb_cancel_schedule(callback: CallbackQuery, state: FSMContext):
    await callback.answer("❌ Отложенный пост отменён", show_alert=False)
    await state.clear()