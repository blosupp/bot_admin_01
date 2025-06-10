from aiogram import Router, types, F
from aiogram.types import CallbackQuery
from database.crud import get_last_logs, clear_logs, get_all_users
from database.crud import add_log

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
    await callback.message.edit_text(text)
