from aiogram.types import Message
from loader import bot
from datetime import datetime
import os


async def save_image(message: Message):
    photo_info = await bot.get_file(message.photo[-1].file_id)
    photo = await bot.download_file(photo_info.file_path)
    path = os.getcwd().replace('\\', '/') + '/dashboard'
    media_root = f'/media/photo/photo_{message.photo[-1].file_id[:10]}.jpg'
    src = path + media_root
    with open(src, 'wb') as new_file:
        new_file.write(photo.read())
    return media_root
