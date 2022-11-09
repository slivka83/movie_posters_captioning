import sqlite3
from aiogram.types import User, Message
from datetime import datetime


async def add_user(user: User):
    connection = sqlite3.connect('dashboard/db.sqlite3')
    cursor = connection.cursor()
    if not cursor.execute(f'SELECT telegram_id from BOT_USERS WHERE telegram_id = {user.id}'):
        info = (user.id, user.username, user.full_name, datetime.now())
        cursor.execute('INSERT INTO BOT_USERS (telegram_id, user_name, full_name, time_create) VALUES (?, ?, ?, ?);',
                       info)
        connection.commit()
        cursor.close()
        return True
    return False


async def add_request(message: Message, filepath: str, response='None'):
    connection = sqlite3.connect('dashboard/db.sqlite3')
    cursor = connection.cursor()
    cursor.execute('SELECT ID FROM BOT_USERS WHERE telegram_id={}'.format(message.from_user.id))
    user_id = cursor.fetchall()[0][0]
    values = (user_id, filepath, response, datetime.now())
    cursor.execute('INSERT INTO BOT_USERSREQUESTS (user_id, image, response, time_create) VALUES (?, ?, ?, ?)',
                   values)

    connection.commit()
    cursor.close()
