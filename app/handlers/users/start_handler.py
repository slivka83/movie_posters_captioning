from loader import dp
from aiogram.types import Message
from utils.db_api.sqllite import add_user, add_request
import logging
from aiogram.types import ContentType
from loader import bot
from utils.image_processing import save_image


@dp.message_handler(commands=['start'])
async def hello_message(message: Message):
    # Add user to db
    await add_user(message.from_user)
    # Starting message
    await message.answer('Hi, {}!'.format(message.from_user.username))


@dp.message_handler(content_types=[ContentType.PHOTO])
async def photo_response(message: Message):
    # Save image
    filepath = await save_image(message)
    # Add to db
    await add_request(message=message, filepath=filepath)
    # Response
    await message.answer("This function isn't working right now :(")
