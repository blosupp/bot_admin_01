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


