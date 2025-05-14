from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


router = Router()

# Временное хранилище (в будущем — база данных)
user_channels = {}

@router.message(Command("add_channel"))
async def add_channel(message: types.Message):
    if not message.forward_from_chat:
        await message.answer("📩 Перешли мне сообщение из канала, который ты хочешь добавить.")
        return

    user_id = message.from_user.id
    channel_id = message.forward_from_chat.id
    channel_title = message.forward_from_chat.title

    user_channels.setdefault(user_id, []).append((channel_id, channel_title))
    await message.answer(f"✅ Канал «{channel_title}» добавлен!")

@router.message(Command("my_channels"))
async def show_channels(message: types.Message):
    user_id = message.from_user.id
    channels = user_channels.get(user_id, [])

    if not channels:
        await message.answer("📭 У тебя пока нет добавленных каналов.")
        return

    keyboard = []
    for chan_id, title in channels:
        keyboard.append([
            InlineKeyboardButton(
                text=f"🗑 Удалить «{title}»",
                callback_data=f"delete_channel:{chan_id}"
            )
        ])

    await message.answer(
        "📋 Твои каналы. Нажми, чтобы удалить:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

@router.callback_query(lambda c: c.data and c.data.startswith("delete_channel:"))
async def delete_channel_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    chan_id = int(callback.data.split(":")[1])

    channels = user_channels.get(user_id, [])
    new_channels = [(id, title) for id, title in channels if id != chan_id]

    if len(new_channels) < len(channels):
        user_channels[user_id] = new_channels
        await callback.answer("✅ Канал удалён.")
        await callback.message.delete()
    else:
        await callback.answer("❌ Канал не найден.")