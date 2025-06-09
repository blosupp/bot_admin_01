from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from bot.keyboards.post_video_keyboard import generate_video_post_keyboard
from database.crud import add_log
router = Router()

# Состояние для видео-поста
class VideoPostState(StatesGroup):
    confirming_post = State()



# Ловим видео от пользователя
@router.message(F.video)
async def handle_video_post(message: Message, state: FSMContext):
    await state.set_state(VideoPostState.confirming_post)
    await message.answer(
        "🔧 Пока видео-посты не поддерживаются.\n"
        "Но ты уже можешь нажимать кнопки (они заглушки).",
        reply_markup=generate_video_post_keyboard()
    )

# Обработчики-заглушки для кнопок
@router.callback_query(VideoPostState.confirming_post)
async def stub_video_buttons(callback: CallbackQuery, state: FSMContext):
    await add_log(
        user_id=callback.from_user.id,
        action_type="stub",
        description="Кнопка видео-поста нажата"
    )
    await callback.answer("🔧 Эта кнопка пока не работает — видео-посты в разработке.")
