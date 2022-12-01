from aiogram.types import Message
from loader import bot, feature_extractor, model, tokenizer
from datetime import datetime
import os
from PIL import Image
import torch


async def save_image(message: Message):
    photo_info = await bot.get_file(message.photo[-1].file_id)
    photo = await bot.download_file(photo_info.file_path)
    path = os.getcwd().replace('\\', '/') + '/dashboard'
    media_root = f'/media/photo/photo_{message.photo[-1].file_id[10:-30]}.jpg'
    src = path + media_root
    with open(src, 'wb') as new_file:
        new_file.write(photo.read())
    return src


async def process_image(image_path):
    max_length = 64
    num_beams = 4
    gen_kwargs = {"max_length": max_length, "num_beams": num_beams}

    device = torch.device("cpu")

    images = []
    i_image = Image.open(image_path)
    i_image = i_image.resize([224, 224])
    if i_image.mode != "RGB":
        i_image = i_image.convert(mode="RGB")

    # model.feat
    images.append(i_image)
    pixel_values = feature_extractor(images=images, return_tensors="pt").pixel_values
    pixel_values = pixel_values.to(device)

    output_ids = model.generate(pixel_values, **gen_kwargs)

    preds = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
    preds = [pred.strip() for pred in preds]
    return preds[0]
