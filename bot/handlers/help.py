from aiogram import Router, types
from aiogram.filters import Command
from database.crud import get_user_role

router = Router()

@router.message(Command("help"))
async def help_command(message: types.Message):
    user_id = message.from_user.id
    role = await get_user_role(user_id)

    base_text = (
        "🤖 <b>Доступные команды:</b>\n\n"

        "<b>📌 Генерация:</b>\n"
        "/generate_text — сгенерировать текст по промпту\n"
        "/generate_photo — 🔧 заглушка\n"
        "/generate_video — 🔧 заглушка\n\n"

        "<b>📤 Посты:</b>\n"
        "/post — начать генерацию и публикацию\n"
        "/schedule_post — создать отложенный пост\n"
        "/scheduled — список запланированных постов\n\n"

        "<b>🧠 Промпты:</b>\n"
        "/prompt — изменить текущий промпт\n"
        "/prompts — список всех промптов\n\n"

        "<b>📡 Каналы:</b>\n"
        "/add_channel — добавить канал\n"
        "/my_channels — список твоих каналов\n\n"

        "<b>💬 Общение:</b>\n"
        "/chatmode — вкл/выкл память\n"
        "/forget — очистить историю\n"
        "/me — информация о себе\n\n"
    )

    admin_text = (
        "<b>🛠 Админ-команды:</b>\n"
        "/add_user <code>user_id</code> — добавить пользователя\n"
        "/remove_user <code>user_id</code> — удалить пользователя\n"
        "/users — список пользователей\n\n"
    )

    superadmin_text = (
        "<b>👑 Команды суперадмина:</b>\n"
        "/add_admin <code>user_id</code> — назначить админа\n"
        "/remove_admin <code>user_id</code> — снять админа\n"
        "/logs — журнал действий\n\n"
    )

    final_text = base_text
    if role == "admin":
        final_text += admin_text
    elif role == "superadmin":
        final_text += admin_text + superadmin_text

    await message.answer(final_text, parse_mode="HTML")
