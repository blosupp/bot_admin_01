from aiogram import Router, types, F
from aiogram.types import CallbackQuery
from database.crud import get_last_logs, clear_logs, get_all_users
from database.crud import add_log
from database.crud import set_user_role, delete_user
from bot.keyboards.user_manage import get_user_manage_buttons
from bot.keyboards.general_manage_keyboard import get_general_manage_keyboard

from aiogram.types import InlineKeyboardMarkup

router = Router()

@router.callback_query(F.data == "view_logs")
async def handle_view_logs(callback: CallbackQuery):
    await add_log(callback.from_user.id, "adminpanel", "просмотрел логи")
    logs = await get_last_logs(limit=10)
    if not logs:
        await callback.message.edit_text("📭 Логи отсутствуют.")
        return

    text = "📜 <b>Последние действия:</b>\n\n"
    for log in logs:
        username = f"@{log.user.username}" if log.user and log.user.username else f"ID: {log.user_id}"
        text += f"• [{log.created_at.strftime('%d.%m.%Y %H:%M')}] {username}: {log.description}\n"
    await callback.message.edit_text(text)


@router.callback_query(F.data == "clear_logs")
async def handle_clear_logs(callback: CallbackQuery):
    await clear_logs()
    await add_log(callback.from_user.id, "adminpanel", "очистил логи")
    await callback.message.edit_text("🧹 Логи успешно очищены.")


@router.callback_query(F.data == "user_management")
async def handle_user_management(callback: CallbackQuery):
    await add_log(callback.from_user.id, "adminpanel", "открыл список пользователей")
    users = await get_all_users()
    if not users:
        await callback.message.edit_text("🙈 Пользователей не найдено.")
        return

    text = "👥 <b>Список пользователей:</b>\n\n"
    for user in users:
        name = f"@{user.username}" if user.username else f"ID: {user.id}"
        text += f"• {name} — <i>{user.role}</i>\n"

    markup = get_general_manage_keyboard()
    await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")


@router.callback_query(F.data.startswith("promote_user:"))
async def handle_promote_user(callback: CallbackQuery):
    user_id = int(callback.data.split(":")[1])
    await set_user_role(user_id, "admin")
    await add_log(callback.from_user.id, "adminpanel", f"назначил пользователя {user_id} админом")
    await callback.answer("✅ Назначен админом")
    await handle_user_management(callback)

@router.callback_query(F.data.startswith("demote_user:"))
async def handle_demote_user(callback: CallbackQuery):
    user_id = int(callback.data.split(":")[1])
    await set_user_role(user_id, "client")
    await add_log(callback.from_user.id, "adminpanel", f"снял пользователя {user_id} с админа")
    await callback.answer("🔕 Админ снят")
    await handle_user_management(callback)

@router.callback_query(F.data.startswith("delete_user:"))
async def handle_delete_user(callback: CallbackQuery):
    user_id = int(callback.data.split(":")[1])
    await delete_user(user_id)
    await add_log(callback.from_user.id, "adminpanel", f"удалил пользователя {user_id}")
    await callback.answer("❌ Удалён")
    await handle_user_management(callback)