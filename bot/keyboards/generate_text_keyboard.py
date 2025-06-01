from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def generate_text_action_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔁 Ещё", callback_data="regen_text"),
            InlineKeyboardButton(text="✏️ Редактировать", callback_data="edit_text"),
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_text_publish")
        ]
    ])
