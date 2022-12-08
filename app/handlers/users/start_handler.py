from loader import dp
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from utils.db_api.sqllite import add_user, add_request, get_last_image_filepath
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
           'Суть проекта - генерация описания к фотографиям.\n' \
           'Чтобы получить описание, просто пришли нам фотографию и мы сгенерируем описание в стиле постера к фильму 😉'.format(
        message.from_user.username)
    await message.answer(text)


@dp.message_handler(content_types=[ContentType.PHOTO])
async def photo_response(message: Message):
    await add_user(message.from_user)
    # Save image
    filepath = await save_image(message)
    # Response
    text_response = await process_image(filepath)
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton(text='Сгенерировать еще!', callback_data='gen'))
    await bot.send_message(text="Вот описание твоей фотографии:\n"
                                f"{text_response}", chat_id=message.from_user.id, reply_markup=markup)
    # Add to db
    await add_request(message=message, filepath=filepath, response=text_response)


@dp.callback_query_handler(text=['gen'])
async def generate_again(call: CallbackQuery):
    await bot.edit_message_reply_markup(
        chat_id=call.from_user.id,
        message_id=call.message.message_id,
        reply_markup=None
    )

    last_image_filepath = await get_last_image_filepath(call)

    # Response
    text_response = await process_image(last_image_filepath, augmentation=True)
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton(text='Сгенерировать еще!', callback_data='gen'))

    await bot.send_message(text="Вот описание твоей фотографии:\n"
                                f"{text_response}", chat_id=call.from_user.id, reply_markup=markup)
    # Add to db
    await add_request(call=call, filepath=last_image_filepath, response=text_response)
