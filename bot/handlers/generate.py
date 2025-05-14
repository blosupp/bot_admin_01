from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from openai import AsyncOpenAI
from database.crud import get_or_create_user, get_active_prompt
from bot.keyboards.generate import generate_action_keyboard
from bot.config import  OPENAI_API_KEY

router = Router()
user_generations = {}

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

class PostState(StatesGroup):
    waiting_for_edit = State()
    waiting_for_datetime = State()

@router.message(F.text.lower() == "/generate")
async def generate_post(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username or "unknown"
    await get_or_create_user(user_id, username)

    prompt = await get_active_prompt(user_id)

    try:
        response = await client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": "Сгенерируй пост по описанию."}
            ],
            temperature=0.7,
            max_tokens=500
        )
        text = response.choices[0].message.content
        user_generations[user_id] = text
        await message.answer(text, reply_markup=generate_action_keyboard())

    except Exception as e:
        await message.answer(f"❌ Ошибка при генерации:\n\n{e}")
