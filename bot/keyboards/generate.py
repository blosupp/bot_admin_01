from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ✅ Клавиатура для действий после генерации фото-поста

def generate_action_keyboard(temp_id: int) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text="🔁 Ещё", callback_data=f"regen_temp:{temp_id}"),
            InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit_temp:{temp_id}"),
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_photo_publish")
        ],
        [
            InlineKeyboardButton(text="📅 Отложить", callback_data=f"schedule_temp:{temp_id}"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_post")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# ✅ Клавиатура выбора канала для публикации

def generate_publish_keyboard(channels: list) -> InlineKeyboardMarkup:
    buttons = []
    for channel_id, title in channels:
        buttons.append([
            InlineKeyboardButton(text=f"📤 {title}", callback_data=f"photo_channel:{channel_id}")
        ])
    buttons.append([
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_post")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)