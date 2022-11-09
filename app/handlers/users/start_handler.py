from loader import dp
from aiogram.types import Message
from utils.db_api.sqllite import add_user, add_request
import logging
from aiogram.types import ContentType
from loader import bot
from utils.image_processing import save_image, process_image


@dp.message_handler(commands=['start'])
async def hello_message(message: Message):
    # Add user to db
    await add_user(message.from_user)
    # Starting message
    text = 'Привет, {}!\n' \
           'Мы команда MPC, приятно познакомиться! ☺\n' \
           'Суть проекта - генерация описания к фильму по его постеру.\n' \
           'Чтобы получить описание, просто пришли нам постер к любому фильму 😉'.format(message.from_user.username)
    await message.answer(text)


@dp.message_handler(content_types=[ContentType.PHOTO])
async def photo_response(message: Message):
    await add_user(message.from_user)
    # Save image
    filepath = await save_image(message)
    # Response
    text_response = await process_image(filepath)
    await message.answer("Вот описание твоего постера:\n"
                         f"{text_response}")
    # Add to db
    # await add_request(message=message, filepath=filepath, response=text_response)
