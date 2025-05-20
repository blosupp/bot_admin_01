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

from bot.handlers import chat



bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


dp.include_router(user.router)
dp.include_router(prompt.router)
dp.include_router(generate.router)
dp.include_router(channels.router)
dp.include_router(prompts.router)
dp.include_router(chat.router)
dp.include_router(post.router)



async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def main():
    print("Бот запускается...")
    await on_startup()
    await dp.start_polling(bot)





if __name__ == "__main__":
    asyncio.run(main())

