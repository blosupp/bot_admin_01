from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.exceptions import TelegramForbiddenError

from database.crud import add_channel, get_user_channels, delete_channel

router = Router()

# Состояние FSM
class ChannelState(StatesGroup):
    waiting_for_forward = State()


# Команда /add_channel
@router.message(Command("add_channel"))
async def add_channel_entry(message: types.Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    args = message.text.split(maxsplit=2)

    # ✅ Вариант 1: ручной ввод
    if len(args) == 3:
        title = args[1]
        channel_id_or_username = args[2]

        try:
            chat = await bot.get_chat(channel_id_or_username)
            member = await bot.get_chat_member(chat.id, bot.id)

            if member.status not in ("administrator", "creator"):
                await message.answer("❌ Я не админ в этом канале. Добавь меня как администратора.")
                return

            await add_channel(owner_id=user_id, title=title, channel_id=chat.id)
            await message.answer(f"✅ Канал «{title}» добавлен вручную.")
            return

        except Exception as e:
            await message.answer(f"❌ Ошибка при получении канала:\n<code>{e}</code>", parse_mode="HTML")
            return

    # 📨 Вариант 2: FSM — ждём пересылку
    await state.set_state(ChannelState.waiting_for_forward)
    await message.answer("📩 Перешли пост из канала, чтобы я добавил его.")


# Обработка пересланного сообщения
@router.message(ChannelState.waiting_for_forward)
async def receive_forwarded_channel(message: types.Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    channel = message.forward_from_chat

    print("➡️ FORWARD DEBUG:", channel)

    if channel is None:
        await message.answer("❌ Не могу определить канал. Убедись, что ты переслал именно пост, а не скопировал текст.")
        return

    title = channel.title
    chat_id = channel.id

    try:
        member = await bot.get_chat_member(chat_id=chat_id, user_id=bot.id)
        if member.status not in ("administrator", "creator"):
            await message.answer("❌ Я не админ в этом канале. Добавь меня как администратора.")
            return
    except TelegramForbiddenError:
        await message.answer("❌ Я не могу проверить канал. Убедись, что я добавлен как админ.")
        return

    await add_channel(owner_id=user_id, title=title, channel_id=chat_id)
    await message.answer(f"✅ Канал «{title}» добавлен по пересылке.")
    await state.clear()


# Показать список каналов
@router.message(Command("my_channels"))
async def list_channels(message: types.Message):
    channels = await get_user_channels(message.from_user.id)
    if not channels:
        await message.answer("📭 У тебя пока нет каналов.")
        return

    keyboard = [
        [
            InlineKeyboardButton(
                text=f"🗑 Удалить «{ch.title}»",
                callback_data=f"delete_channel:{ch.id}"
            )
        ] for ch in channels
    ]

    await message.answer("📋 Твои каналы:", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))


# Удалить канал
@router.callback_query(F.data.startswith("delete_channel:"))
async def delete_channel_callback(callback: types.CallbackQuery):
    channel_id = int(callback.data.split(":")[1])
    user_id = callback.from_user.id

    await delete_channel(channel_id=channel_id, owner_id=user_id)

    await callback.answer("✅ Удалено.")
    await callback.message.delete()