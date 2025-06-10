# keyboards/adminpanel_keyboard.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_admin_panel_keyboard(role: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="📜 Показать логи", callback_data="view_logs")],
        [InlineKeyboardButton(text="🧹 Очистить логи", callback_data="clear_logs")]
    ]

    if role == "superadmin":
        buttons.append([
            InlineKeyboardButton(text="👥 Пользователи", callback_data="user_management")
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)
