from openai import AsyncOpenAI
from bot.config import OPENAI_API_KEY
from database.crud import get_active_prompt
from database.db import AsyncSessionLocal

from sqlalchemy import delete, select
from database.models import Message

client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def generate_text(prompt: str, max_tokens: int = 700) -> str:
    """
    Генерирует текст с GPT-4-turbo
    :param prompt: текст запроса
    :param max_tokens: макс. длина ответа
    :return: сгенерированный текст или ошибка
    """
    try:
        response = await client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Ты — AI-ассистент, пиши кратко, понятно и по теме."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"❌ Ошибка при генерации: {e}"


async def generate_post_text(user_id: int) -> str:
    """
    Берёт активный промпт из базы и генерирует пост.
    """
    async with AsyncSessionLocal() as session:
        prompt = await get_active_prompt(session, user_id)

    if not prompt or not prompt.text:
        return "❌ У тебя не задан активный промпт. Установи его командой /prompt"

    return await generate_text(prompt.text)


from database.crud import get_last_messages, add_message
from database.db import get_async_session

async def generate_text_with_memory(user_id: int, new_user_text: str) -> str:
    async with get_async_session() as session:
        print(f"⚙️ [user_id={user_id}] → {new_user_text}")

        history = await get_last_messages(session, user_id)
        print("📚 История из БД:", [(m.role, m.content[:30]) for m in history])

        messages = [{"role": "system", "content": "Ты — AI-ассистент, веди диалог кратко."}]
        for m in history:
            messages.append({"role": m.role, "content": m.content})
        messages.append({"role": "user", "content": new_user_text})

        try:
            response = await client.chat.completions.create(
                model="gpt-4-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=700
            )
            reply = response.choices[0].message.content.strip()

            print("🧠 GPT ответ:", reply[:50])

            # 💾 Сохраняем диалог
            await add_message(session, user_id, "user", new_user_text)
            await add_message(session, user_id, "assistant", reply)

            # 🧹 Удаляем всё лишнее — оставляем только последние 50
            subquery = (
                select(Message.id)
                .where(Message.user_id == user_id)
                .order_by(Message.id.desc())
                .limit(50)
            ).subquery()

            await session.execute(
                delete(Message)
                .where(Message.user_id == user_id)
                .where(Message.id.not_in(select(subquery.c.id)))
            )
            await session.commit()

            return reply

        except Exception as e:
            print("❌ GPT ошибка:", e)
            return f"❌ Ошибка: {e}"
