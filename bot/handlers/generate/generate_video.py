from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command("generate_video"))
async def generate_video_stub(message: types.Message):
    await message.answer("🔧 Генерация видео пока не реализована.")
