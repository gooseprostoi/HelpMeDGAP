import asyncio
from aiogram import Bot, Dispatcher
import sqlite3
from app.handlers import router
from config import TOKEN_API, ADMIN_ID
import os
import logging

bot = Bot(TOKEN_API)
dp = Dispatcher()
current_file = os.path.realpath(__file__)
path = os.path.dirname(current_file) + '/'


async def main():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - [%(levelname)s] - %(name)s -"
                               "(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s")
    dp.include_router(router)
    conn = sqlite3.connect('HelpMeDGAP.sql')
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS consultations (
        username VARCHAR(50), 
        course INT(1), 
        subject VARCHAR(50), 
        description TEXT, 
        form_submission_time TEXT,
        form_response_time TEXT,
        tutor_username VARCHAR(50),
        finished INT(1),
        consultation_finish_time TEXT)""")
    conn.commit()
    cur.close()
    conn.close()
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        print('Exit')


if __name__ == '__main__':
    asyncio.run(main())