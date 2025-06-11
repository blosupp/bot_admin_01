# bot/keyboards/user_manage.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_user_manage_buttons(viewer_id: int, target_id: int, target_role: str) -> InlineKeyboardMarkup | None:
    if target_id == viewer_id or target_role == "superadmin":
        return None

    buttons = []

    if target_role in ("client", "user"):  # ✅ добавили user
        buttons.append(InlineKeyboardButton(text="🟢 Админ", callback_data=f"promote_user:{target_id}"))
    elif target_role == "admin":
        buttons.append(InlineKeyboardButton(text="🔴 Снять", callback_data=f"demote_user:{target_id}"))

    buttons.append(InlineKeyboardButton(text="❌ Удалить", callback_data=f"delete_user:{target_id}"))

    return InlineKeyboardMarkup(inline_keyboard=[buttons])