from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from bot.states.post_states import SchedulePostState
from database.crud import get_temp_post, delete_temp_post, create_scheduled_post
from database.crud import get_scheduled_posts_by_user

from database.crud import add_log

router = Router()

@router.message(SchedulePostState.confirming, F.text.lower() == "подтвердить")
async def handle_confirm_schedule(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()

    scheduled_time = data.get("scheduled_time")
    channel_id = data.get("channel_id")

    if not scheduled_time or not channel_id:
        await message.answer("❗ Не хватает данных для планирования.")
        return

    temp_post = await get_temp_post(user_id)
    if not temp_post:
        await message.answer("❗ Временный пост не найден.")
        return

    await create_scheduled_post(
        user_id=user_id,
        channel_id=channel_id,
        caption=temp_post.caption,
        file_id=temp_post.file_id,
        scheduled_time=scheduled_time
    )

    await delete_temp_post(user_id)
    await add_log(
        user_id=user_id,
        action_type="schedule",
        description=f"Пост запланирован на {scheduled_time} в канал {channel_id}"
    )
    await message.answer("✅ Пост запланирован. Временный черновик удалён.")
    await state.clear()


@router.message(SchedulePostState.choosing_channel)
async def handle_schedule_choose_channel(message: Message, state: FSMContext):
    try:
        channel_id = int(message.text.strip())  # 👈 временная заглушка
    except ValueError:
        await message.answer("⚠️ Введите ID канала числом.")
        return

    await state.update_data(channel_id=channel_id)

    await message.answer(
        "📅 Введите дату и время публикации в формате: <b>01.07.2025 14:30</b>",
        parse_mode="HTML"
    )
    await state.set_state(SchedulePostState.choosing_datetime)


@router.message(F.text == "/scheduled")
async def show_scheduled_posts(message: Message):
    user_id = message.from_user.id
    posts = await get_scheduled_posts_by_user(user_id)

    if not posts:
        await message.answer("📭 У вас нет запланированных постов.")
        return

    text = "<b>📌 Ваши запланированные посты:</b>\n\n"
    for post in posts:
        time = post.scheduled_time.strftime("%d.%m.%Y %H:%M")
        preview = post.caption[:50] + "..." if post.caption else "📷 [медиа]"
        text += f"🗓 <b>{time}</b> → <i>{preview}</i>\n"

    await message.answer(text, parse_mode="HTML")