from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def generate_photo_action_keyboard(temp_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔁 Ещё", callback_data=f"regen_temp:{temp_id}"),
            InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit_temp:{temp_id}"),
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_photo_publish")
        ],
        [
            InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_post")
        ]
    ])

def generate_photo_publish_keyboard(channels: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=f"📤 {title}", callback_data=f"photo_channel:{channel_id}")]
        for channel_id, title in channels
    ]
    buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_post")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def generate_photo_schedule_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏰ Запланировать", callback_data="schedule_post")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_post")],
    ])
