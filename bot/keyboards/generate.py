from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def generate_action_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text="🔁 Ещё", callback_data="regenerate"),
            InlineKeyboardButton(text="✏️ Редактировать", callback_data="edit"),
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm")
        ],
        [
            InlineKeyboardButton(text="📅 Отложить", callback_data="schedule"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def generate_publish_keyboard(channels: list) -> InlineKeyboardMarkup:
    buttons = []
    for channel_id, title in channels:
        buttons.append([
            InlineKeyboardButton(text=f"📤 {title}", callback_data=f"publish:{channel_id}")
        ])
    buttons.append([
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)