import asyncio
from aiogram import Bot, Dispatcher
from bot.config import BOT_TOKEN
from bot.handlers import user  # импортируем user router
from bot.handlers import user, prompt, generate  # <— добавили prompt
from aiogram.fsm.storage.memory import MemoryStorage
from bot.handlers import user, prompt, generate, channels, post
from bot.keyboards import generate as kb_generate
from database.db import engine, Base
from bot.handlers import prompts
from scheduler.post_scheduler import scheduler, check_scheduled_posts
from apscheduler.triggers.interval import IntervalTrigger
from bot.handlers import queue


from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.handlers import chat
import logging



bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

@dp.callback_query()
async def debug_all(callback: CallbackQuery, state: FSMContext):
    print("🔥 Callback data:", callback.data)
    print("🔥 FSM state:", await state.get_state())
    await callback.answer("DEBUG: кнопка нажата")
dp.include_router(user.router)
dp.include_router(prompt.router)
dp.include_router(generate.router)
dp.include_router(channels.router)
dp.include_router(prompts.router)
dp.include_router(chat.router)
dp.include_router(post.router)
dp.include_router(queue.router)





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

