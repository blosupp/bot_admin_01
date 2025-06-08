
from aiogram import Router, types
from aiogram.filters import Command
from scheduler.post_scheduler import check_scheduled_posts

router = Router()

@router.message(Command("run_scheduler"))
async def run_scheduler_command(message: types.Message):
    await message.answer("🔄 Проверяю отложенные посты...")
    await check_scheduled_posts()
    await message.answer("✅ Проверка завершена.")
