from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command("generate_photo"))
async def generate_photo_stub(message: types.Message):
    await message.answer("🔧 Генерация по фото пока не реализована.")
