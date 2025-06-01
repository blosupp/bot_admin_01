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
    choosing_channel = State()
    choosing_datetime = State()  # пользователь вводит дату и время
    confirming = State()         # подтверждение перед сохранением


class PhotoPostState(StatesGroup):
    choosing_channel = State()
    confirming_post = State()

class TextPostState(StatesGroup):
    """Состояния для генерации и подтверждения текстового поста"""
    waiting_for_prompt = State()
    confirming = State()


class EditTextPost(StatesGroup):
    """Состояние для ввода финального текста при редактировании"""
    waiting_for_new_text = State()