from aiogram import Router, types, F
from aiogram.filters import Command
from database.crud import get_all_prompts, activate_prompt, delete_prompt

router = Router()

@router.message(Command("prompts"))
async def list_prompts(message: types.Message):
    user_id = message.from_user.id
    prompts = await get_all_prompts(user_id)

    if not prompts:
        await message.answer("📭 У тебя пока нет сохранённых промптов.")
        return

    for p in prompts:
        text = f"🧠 <b>{'🟢 Активный' if p.is_active else '—'}</b>\n<code>{p.text}</code>"
        keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[[
                types.InlineKeyboardButton(text="🟢 Сделать активным", callback_data=f"activate:{p.id}"),
                types.InlineKeyboardButton(text="❌ Удалить", callback_data=f"delete:{p.id}")
            ]]
        )
        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

@router.callback_query(F.data.startswith("activate:"))
async def handle_activate(callback: types.CallbackQuery):
    prompt_id = int(callback.data.split(":")[1])
    user_id = callback.from_user.id
    await activate_prompt(prompt_id, user_id)
    await callback.answer("✅ Промпт активирован!")
    await callback.message.delete()

@router.callback_query(F.data.startswith("delete:"))
async def handle_delete(callback: types.CallbackQuery):
    prompt_id = int(callback.data.split(":")[1])
    user_id = callback.from_user.id
    await delete_prompt(prompt_id, user_id)
    await callback.answer("🗑️ Удалено")
    await callback.message.delete()
