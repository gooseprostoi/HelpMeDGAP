from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from jinja2 import Environment, FileSystemLoader
import sqlite3
import app.keyboards as kb
from app.utilits import Form, MainData
from config import TUTORCHAT_ID, ADMIN_ID, TUTORCHANNEL_ID
import app.subject_data as sbj
import datetime
from aiogram.types import FSInputFile

router = Router()
from main import bot, path

conn = sqlite3.connect(path + 'HelpMeDGAP.sql')
cur = conn.cursor()

env = Environment(loader=FileSystemLoader(path + 'app/texts'))  # нужно для jinja


def get_subject_name(course_: int, subject_: str) -> str:  # чтобы получать нормальные названия предметов, а не GenPhys1
    return sbj.subject_1[f'course_{course_}'][f'{subject_}']  # поменять subject_1 на subject_2 весной


env.filters['get_subject_name'] = get_subject_name


# start-----------------------------------------------------------------------------------------------------------------
@router.message(F.text == '/start')
async def start(message: Message) -> None:
    if message.chat.id != TUTORCHAT_ID:
        await message.answer(text=open(path + 'app/texts/start.txt', 'r', encoding='UTF-8').read(), parse_mode='HTML',
                             reply_markup=kb.start_brd)


@router.callback_query(F.data == 'cancel|start')
async def start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(text=open(path + 'app/texts/start.txt', 'r', encoding='UTF-8').read(),
                                     parse_mode='HTML',
                                     reply_markup=kb.start_brd)


# sign_up---------------------------------------------------------------------------------------------------------------

@router.callback_query(F.data == 'sign_up')
@router.callback_query(F.data == 'cancel|course')
async def course(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(username=callback.from_user.username)
    await state.set_state(Form.course)
    await callback.message.edit_text(text=open(path + 'app/texts/course.txt', 'r', encoding='UTF-8').read(),
                                     parse_mode='HTML',
                                     reply_markup=await kb.get_course_brd())


@router.callback_query(Form.course)
@router.callback_query(F.data == 'cancel|subject')
async def subject(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.data == 'cancel|subject':
        form = await state.update_data()
        COURSE = form['course']
    else:
        COURSE = int(callback.data.split('|')[1])
        await state.update_data(course=COURSE)
    await state.set_state(Form.subject)
    await callback.message.edit_text(text=open(path + 'app/texts/subject.txt', 'r', encoding='UTF-8').read(),
                                     parse_mode='HTML',
                                     reply_markup=kb.get_subject_brd(COURSE))


@router.callback_query(Form.subject)
@router.callback_query(F.data == 'cancel|description')
async def description(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.data != 'cancel|description':
        await state.update_data(subject=callback.data.split('|')[1])
        await state.set_state(Form.edit_message_id)  # костыль, чтобы изменить сообщение после отправки описания
        await state.update_data(edit_message_id=callback.message.message_id)  # костыль
    await state.set_state(Form.description)
    await callback.message.edit_text(text=open(path + 'app/texts/description.txt', 'r', encoding='UTF-8').read(),
                                     parse_mode='HTML',
                                     reply_markup=kb.description_brd,
                                     disable_web_page_preview=True)


@router.message(Form.description)
async def form_checking(message: Message, state: FSMContext) -> None:
    form = await state.update_data(description=message.text)
    await state.set_state(Form.passage)  # костыль, чтобы перетащить на следующий

    tm = env.get_template('form_checking.txt')
    await message.delete()
    await bot.edit_message_text(chat_id=message.chat.id, message_id=form['edit_message_id'], parse_mode='HTML',
                                text=tm.render(form=form),
                                reply_markup=kb.form_checking_brd)


@router.callback_query(Form.passage)
async def form_submitted(callback: CallbackQuery, state: FSMContext) -> None:
    form = await state.update_data()
    cur.execute(
        """INSERT INTO consultations (username, course, subject, description, form_submission_time) VALUES (?, ?, ?, ?, datetime(?))""",
        (form['username'], form['course'], form['subject'], form['description'], datetime.datetime.now()))
    conn.commit()

    callback_data = MainData(state='submitted', form_id=cur.lastrowid, user_id=callback.from_user.id)

    tm = env.get_template('dangling_form.txt')
    tmp_str = tm.render(form=form)  # нужно сначала сгенерировать, а потом уничтожать form
    await state.clear()
    await bot.send_message(chat_id=TUTORCHANNEL_ID, text=tmp_str, parse_mode='HTML',
                           reply_markup=await kb.get_accepting_brd(callback_data))
    await callback.message.edit_text(text=open(path + 'app/texts/form_submitted.txt', 'r', encoding='UTF-8').read(),
                                     parse_mode='HTML',
                                     reply_markup=kb.form_submitted_brd)


@router.callback_query(MainData.filter(F.state == 'submitted'))
async def form_accepted(callback: CallbackQuery, callback_data: MainData) -> None:
    await bot.delete_message(chat_id=TUTORCHANNEL_ID, message_id=callback.message.message_id)
    cur.execute("""UPDATE consultations SET form_response_time = datetime(?), tutor_username = ? WHERE rowid = ?""",
                (datetime.datetime.now(), callback.from_user.username, callback_data.form_id))
    conn.commit()

    tm_tutor = env.get_template('form_accepted_tutor.txt')
    tm_user = env.get_template('form_accepted_user.txt')
    callback_data.state = 'accepted'

    cur.execute("""SELECT * FROM consultations WHERE rowid = ?""", (callback_data.form_id,))
    form = cur.fetchall()[0]

    await bot.send_message(chat_id=callback.from_user.id, parse_mode='HTML',
                           text=tm_tutor.render(form=form, subject=get_subject_name(form[1], form[2])),
                           reply_markup=await kb.get_consultation_state_brd(callback_data))
    await bot.send_message(chat_id=callback_data.user_id, parse_mode='HTML',
                           text=tm_user.render(tutor_username=form[6]),
                           reply_markup=kb.close_brd)


@router.callback_query(F.data == 'close')
async def close_message(callback: CallbackQuery) -> None:
    await callback.message.delete()


@router.callback_query(MainData.filter(F.state == 'accepted'))
async def consultation_completed(callback: CallbackQuery, callback_data: MainData) -> None:
    cur.execute("""UPDATE consultations SET  finished = ?, consultation_finish_time = datetime(?) WHERE rowid = ?""",
                (callback_data.finished, datetime.datetime.now(), callback_data.form_id))
    conn.commit()

    await callback.answer(
        text='Консультация ' + (lambda x: 'завершена' if x == 1 else 'отменена' if x == -1 else 'ошибка')(
            callback_data.finished))
    await callback.message.delete()


# consultation_list-----------------------------------------------------------------------------------------------------------------------


@router.callback_query(F.data == 'consultation_list')
async def consultation_list(callback: CallbackQuery) -> None:
    cur.execute("""SELECT * FROM consultations WHERE username == ? and finished is null""",
                (callback.from_user.username,))
    consul_list = cur.fetchall()
    tm = env.get_template('consultation_list.txt')
    await callback.message.edit_text(
        text=tm.render(consul_list=consul_list),
        parse_mode='HTML',
        reply_markup=kb.consultation_list_brd)


@router.callback_query(F.data == 'consultation_list_extended')
async def consultation_list_extended(callback: CallbackQuery) -> None:
    cur.execute("""SELECT * FROM consultations WHERE username == ?""", (callback.from_user.username,))
    consul_list = cur.fetchall()
    tm = env.get_template('consultation_list_extended.txt')
    await callback.message.edit_text(text=tm.render(consul_list=consul_list), parse_mode='HTML',
                                     reply_markup=kb.consultation_list_extended_brd)


# bags-----------------------------------------------------------------------------------------------------------------------


@router.callback_query(F.data == 'bags')
async def bags(callback: CallbackQuery) -> None:
    await callback.message.edit_text(text=open(path + 'app/texts/bags.txt', 'r', encoding='UTF-8').read(),
                                     parse_mode='HTML',
                                     reply_markup=kb.to_start_brd)


# faq-----------------------------------------------------------------------------------------------------------------------


@router.callback_query(F.data == 'faq')
async def faq(callback: CallbackQuery) -> None:
    await callback.message.edit_text(text=open(path + 'app/texts/faq.txt', 'r', encoding='UTF-8').read(),
                                     parse_mode='HTML',
                                     reply_markup=kb.to_start_brd)


# admin_panel-----------------------------------------------------------------------------------------------------------

@router.message(F.text == '/admin')
async def admin_panel(message: Message):
    await message.delete()
    if message.from_user.id not in ADMIN_ID:
        await message.answer(text='Доступ ограничен',
                             reply_markup=kb.close_brd)
    else:
        cat = FSInputFile(path + "HelpMeDGAP.sql")
        await bot.send_document(chat_id=message.from_user.id, document=cat, caption='SQL-таблица с консультациями',
                                reply_markup=kb.admin_brd)


@router.callback_query(F.data == '/admin')
async def admin_panel(callback: CallbackQuery):
    cat = FSInputFile("HelpMeDGAP.sql")
    await bot.send_document(chat_id=callback.message.from_user.id, document=cat, caption='SQL-таблица с консультациями',
                            reply_markup=kb.admin_brd)


@router.callback_query(F.data == 'recent_forms')
async def recent_forms(callback: CallbackQuery) -> None:
    cur.execute("""SELECT * FROM consultations ORDER BY rowid LIMIT 10""")
    RECENT_FORMS = cur.fetchall()
    print(RECENT_FORMS)
    tm = env.get_template('recent_forms.txt')
    await callback.message.answer(text=tm.render(recent_forms=RECENT_FORMS),
                                  parse_mode='HTML',
                                  reply_markup=kb.close_brd)


# send_chat_id----------------------------------------------------------------------------------------------------------

@router.message(F.text == '/send_chat_id')
async def send_chat_id(message: Message):
    await message.answer(text=f'chat_id: {message.chat.id}')

# sqlalchemy
