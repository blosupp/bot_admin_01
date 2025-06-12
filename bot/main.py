import asyncio
from aiogram import Bot, Dispatcher
from bot.config import BOT_TOKEN
from bot.handlers import user  # импортируем user router
from bot.handlers import user, prompt, generate  # <— добавили prompt
from aiogram.fsm.storage.memory import MemoryStorage
from bot.handlers import user, prompt, channels
from database.db import engine, Base
from bot.handlers import prompts
from scheduler.post_scheduler import scheduler, check_scheduled_posts
from apscheduler.triggers.interval import IntervalTrigger
from bot.handlers import queue



from bot.handlers.generate.generate_text import router as generate_text_router
from bot.handlers.generate.generate_video import router as generate_video_router
from bot.handlers.generate.generate_photo import router as generate_photo_router

from bot.handlers.post.post_photo import router as post_photo_router
from bot.handlers.post.post_video import router as post_video_router
from bot.handlers.post.post_text import router as post_text_router
from bot.handlers.post.scheduler_control import router as scheduler_control_router



from bot.handlers.help import router as help_router
from bot.handlers import schedule
from bot.handlers import superadmin
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.middlewares.register_check import RegisterCheckMiddleware
from bot.handlers.adminpanel import router as adminpanel_router
from bot.handlers.admin_callbacks import router as admin_callback_router



from bot.handlers import chat
import logging



bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)



dp.include_router(channels.router)
dp.include_router(help_router)
dp.include_router(generate_video_router)
dp.include_router(generate_photo_router)
dp.include_router(generate_text_router)
dp.include_router(post_video_router)
dp.include_router(post_photo_router)
dp.include_router(post_text_router)
dp.include_router(scheduler_control_router)
dp.include_router(chat.router)
dp.include_router(user.router)
dp.include_router(prompt.router)
dp.include_router(prompts.router)
dp.include_router(queue.router)
dp.include_router(schedule.router)
dp.include_router(superadmin.router)
dp.message.middleware(RegisterCheckMiddleware())
dp.include_router(adminpanel_router)
dp.include_router(admin_callback_router)





async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        scheduler.add_job(check_scheduled_posts, IntervalTrigger(seconds=60))
        scheduler.start()

async def main():
    print("Бот запускается...")
    try:
        await dp.start_polling(bot)
    except (KeyboardInterrupt, asyncio.CancelledError):
        logging.info("🛑 Бот остановлен вручную или отменён.")




if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("⛔ Бот завершён пользователем.")

