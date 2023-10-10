from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.utilits import MainData
import app.subject_data as sbj

# start--------------------------------------------------------------------------------
start_kb = [
    [InlineKeyboardButton(text='✍️Получить консультацию', callback_data='sign_up')],
    [InlineKeyboardButton(text='🗂Мои консультации', callback_data='consultation_list')],
    [InlineKeyboardButton(text='🪲Ошибки и баги', callback_data='bags'),
     InlineKeyboardButton(text='🔍FAQ', callback_data='faq')]
]

start_brd = InlineKeyboardMarkup(inline_keyboard=start_kb)


# course-------------------------------------------------------------------------------

async def get_course_brd():
    kb_builder = InlineKeyboardBuilder()
    for i in (1, 2, 3):
        kb_builder.button(text=f'{i} курс', callback_data=f'course|{i}')
    kb_builder.button(text='◀️Назад', callback_data='cancel|start')
    kb_builder.adjust(1, 2, 1)
    return kb_builder.as_markup()


# subject------------------------------------------------------------------------------

def get_subject_brd(course: int) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    for i in sbj.subject_1[f'course_{course}']:  # во весной сменить subject_1 на subject_2
        kb_builder.button(text=sbj.subject_1[f'course_{course}'][i], callback_data=f'subject|{i}')
    kb_builder.button(text='◀️Назад', callback_data='cancel|course')
    if course == 1:
        kb_builder.adjust(2, 2, 1)
    elif course == 2:
        kb_builder.adjust(3, 3, 1)
    elif course == 3:
        kb_builder.adjust(3, 3, 2, 1)
    return kb_builder.as_markup()


# description--------------------------------------------------------------------------

description_kb = ([
    [InlineKeyboardButton(text='◀️Назад', callback_data='cancel|subject')]
])

description_brd = InlineKeyboardMarkup(inline_keyboard=description_kb)

#  form_checking-----------------------------------------------------------------------

form_checking_kb = ([
    [InlineKeyboardButton(text='✅Всё правильно', callback_data='.'),
     InlineKeyboardButton(text='◀️Назад', callback_data='cancel|description')]
])

form_checking_brd = InlineKeyboardMarkup(inline_keyboard=form_checking_kb)


# form_submitted-----------------------------------------------------------------------


async def get_accepting_brd(callback_data: MainData):
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Откликнуться', callback_data=callback_data)
    return kb_builder.as_markup()


form_submitted_kb = ([
    [InlineKeyboardButton(text='◀️На главное меню', callback_data='cancel|start')]
])

form_submitted_brd = InlineKeyboardMarkup(inline_keyboard=form_submitted_kb)


# form_accepted-------------------------------------------------------------------------


async def get_consultation_state_brd(callback_data: MainData):
    def tmp_f(x: int, callback_data_: MainData) -> MainData:
        callback_data_.finished = x
        return callback_data_

    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Завершена', callback_data=tmp_f(1, callback_data))
    kb_builder.button(text='Отменена', callback_data=tmp_f(-1, callback_data))
    return kb_builder.as_markup()


# close_notification-------------------------------------------------------------------

close_kb = ([
    [InlineKeyboardButton(text='Закрыть', callback_data='close')]
])

close_brd = InlineKeyboardMarkup(inline_keyboard=close_kb)

# consultation_list--------------------------------------------------------------------


consultation_list_kb = ([
    [InlineKeyboardButton(text='📋Показать все консультации', callback_data='consultation_list_extended')],
    [InlineKeyboardButton(text='◀️Назад', callback_data='cancel|start')]
])

consultation_list_brd = InlineKeyboardMarkup(inline_keyboard=consultation_list_kb)

consultation_list_extended_kb = ([
    [InlineKeyboardButton(text='◀️Назад', callback_data='consultation_list')]
])

consultation_list_extended_brd = InlineKeyboardMarkup(inline_keyboard=consultation_list_extended_kb)

# bags, faq and admin_panel---------------------------------------------------------------------------------

to_start_kb = ([
    [InlineKeyboardButton(text='◀️Назад', callback_data='cancel|start')]
])

to_start_brd = InlineKeyboardMarkup(inline_keyboard=to_start_kb)


# admin_keyboard---------------------------------------------------------------------------------------------

admin_kb = ([
    [InlineKeyboardButton(text='Недавние анкеты', callback_data='recent_forms')],
    [InlineKeyboardButton(text='Закрыть', callback_data='close')]
])

admin_brd = InlineKeyboardMarkup(inline_keyboard=admin_kb)
