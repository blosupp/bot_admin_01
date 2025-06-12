from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_general_manage_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="🟢 Назначить админа", switch_inline_query_current_chat="/add_admin @username"),
            InlineKeyboardButton(text="🔴 Снять админа", switch_inline_query_current_chat="/remove_admin @username"),
        ],
        [
            InlineKeyboardButton(text="➕ Добавить клиента", switch_inline_query_current_chat="/add_user @username"),
            InlineKeyboardButton(text="❌ Удалить клиента", switch_inline_query_current_chat="/remove_user @username"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
