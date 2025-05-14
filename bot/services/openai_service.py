from openai import AsyncOpenAI
from bot.config import OPENAI_API_KEY

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
            model="gpt-4-turbo",  # turbo = быстрее и дешевле
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
