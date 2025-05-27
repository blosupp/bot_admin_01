# bot/states/post_states.py

from aiogram.fsm.state import StatesGroup, State

class EditPhotoPost(StatesGroup):
    waiting_for_new_text = State()

class PostState(StatesGroup):
    choosing_channel = State()
    confirming_post = State()


class SchedulePostState(StatesGroup):
    """
    🕒 Состояния для отложенной публикации
    """
    choosing_datetime = State()  # пользователь вводит дату и время
    confirming = State()         # подтверждение перед сохранением