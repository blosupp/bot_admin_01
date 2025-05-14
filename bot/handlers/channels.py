from aiogram import Router, types
from aiogram.filters import Command

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

    text = "📋 Твои каналы:\n\n"
    for idx, (chan_id, title) in enumerate(channels, 1):
        text += f"{idx}. {title} (`{chan_id}`)\n"

    await message.answer(text, parse_mode="Markdown")
