from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import StatesGroup, State


class Form(StatesGroup):
    username = State()
    course = State()
    edit_message_id = State()  # костыль, чтобы изменять сообщение
    subject = State()
    description = State()
    passage = State()  # костыль, чтобы сделать проверку
    # submitting_date


class MainData(CallbackData, prefix='tutor_form'):
    state: str
    form_id: int
    user_id: int
    tutor_username: str = '.'
    finished: int = 0
