from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select
from datetime import datetime
from bot.config import BOT_TOKEN
from aiogram import Bot
from database.models import ScheduledPost
from database.db import get_async_session
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.crud import delete_temp_post


scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
bot = Bot(token=BOT_TOKEN)

async def check_scheduled_posts():
    """
    ⏰ Проверяет таблицу на готовые к публикации посты
    """
    async with get_async_session() as session:
        now = datetime.utcnow()
        result = await session.execute(
            select(ScheduledPost).where(ScheduledPost.scheduled_time <= now, ScheduledPost.sent == False)
        )
        posts = result.scalars().all()

        for post in posts:
            try:
                print(f"🕒 Проверка отложки: post_id={post.id}, канал={post.channel_id}, "
                      f"время_публикации={post.scheduled_time}, сейчас={datetime.utcnow()}, "
                      f"тип={'фото' if post.file_id else 'текст'}")
                if post.file_id:
                    await bot.send_photo(chat_id=post.channel_id, photo=post.file_id, caption=post.caption[:1024])
                else:
                    await bot.send_message(chat_id=post.channel_id, text=post.caption)

                post.sent = True
                await session.commit()


            except Exception as e:
                print(f"❌ Ошибка при публикации отложенного поста: {e}")
