import sqlite3
from aiogram.types import User, Message, CallbackQuery
from datetime import datetime


async def add_user(user: User):
    connection = sqlite3.connect('dashboard/db.sqlite3')
    cursor = connection.cursor()
    if not cursor.execute(f'SELECT telegram_id from BOT_USERS WHERE telegram_id = {user.id}').fetchall():
        info = (user.id, user.username, user.full_name, datetime.now())
        cursor.execute('INSERT INTO BOT_USERS (telegram_id, user_name, full_name, time_create) VALUES (?, ?, ?, ?);',
                       info)
        connection.commit()
        cursor.close()
        return True
    return False


async def add_request(filepath: str, response='None', message:Message = None, call: CallbackQuery = None):
    if message:
        telegram_id = message.from_user.id
    else:
        telegram_id = call.from_user.id
    connection = sqlite3.connect('dashboard/db.sqlite3')
    cursor = connection.cursor()
    cursor.execute('SELECT ID FROM BOT_USERS WHERE telegram_id={}'.format(telegram_id))
    user_id = cursor.fetchall()[0][0]
    values = (user_id, filepath, response, datetime.now())
    cursor.execute('INSERT INTO BOT_USERSREQUESTS (user_id, image, response, time_create) VALUES (?, ?, ?, ?)',
                   values)

    connection.commit()
    cursor.close()


async def get_last_image_filepath(call: CallbackQuery):
    connection = sqlite3.connect('dashboard/db.sqlite3')
    cursor = connection.cursor()
    cursor.execute('SELECT ID FROM BOT_USERS WHERE telegram_id={}'.format(call.from_user.id))
    user_id = cursor.fetchall()[0][0]
    cursor.execute(f'SELECT IMAGE FROM BOT_USERSREQUESTS WHERE USER_ID = {user_id}')
    filepath = cursor.fetchall()[-1][0]

    cursor.close()
    return filepath