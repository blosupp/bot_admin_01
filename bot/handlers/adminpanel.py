from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup
from database.crud import add_log

from bot.keyboards.adminpanel_keyboard import get_admin_panel_keyboard
from database.crud import get_user_by_id

router = Router()

@router.message(Command("adminpanel"))
async def show_admin_panel(message: types.Message):
    user = await get_user_by_id(message.from_user.id)
    if not user or user.role not in ["admin", "superadmin"]:
        return await message.answer("⛔️ У вас нет доступа к админ-панели.")

    keyboard = get_admin_panel_keyboard(user.role)
    await message.answer("🛠 Админ-панель:", reply_markup=keyboard)
    await add_log(message.from_user.id, "adminpanel", "открыл панель")


# keyboards/adminpanel_keyboard.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_admin_panel_keyboard(role: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="📜 Показать логи", callback_data="view_logs")],
        [InlineKeyboardButton(text="🧹 Очистить логи", callback_data="clear_logs")]
    ]

    if role == "superadmin":
        buttons.append([InlineKeyboardButton(text="👥 Пользователи", callback_data="user_management")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)