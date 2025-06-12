# bot/keyboards/user_manage.py
# ⚠ Архив: индивидуальные кнопки для каждого пользователя
#from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
#from typing import Optional
#
#def get_user_manage_buttons(viewer_id: int, target_id: int, target_role: str, target_username: Optional[str]) -> InlineKeyboardMarkup | None:
#    if target_id == viewer_id or target_role == "superadmin":
#        return None
#
#    username = f"@{target_username}" if target_username else str(target_id)
#
#    if target_role == "admin":
#        text = "🔴 Снять админа"
#        command = f"/remove_admin {username}"
#    elif target_role in ("client", "user"):
#        text = "🟢 Назначить админом"
#        command = f"/add_admin {username}"
#    else:
#        text = "❌ Удалить"
#        command = f"/remove_user {username}"
#
#    buttons = [
#        [InlineKeyboardButton(text=text, switch_inline_query_current_chat=command)]
#    ]
#
#    return InlineKeyboardMarkup(inline_keyboard=buttons)