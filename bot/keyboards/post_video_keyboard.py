from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def generate_video_post_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Опубликовать", callback_data="video_publish"),
            InlineKeyboardButton(text="♻️ Снова", callback_data="video_regen"),
            InlineKeyboardButton(text="✏️ Редактировать", callback_data="video_edit")
        ],
        [
            InlineKeyboardButton(text="⏰ Отложить", callback_data="video_schedule"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="video_cancel")
        ]
    ])