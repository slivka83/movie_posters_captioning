from PIL import Image
import torch
from transformers import AutoTokenizer, ViTFeatureExtractor, VisionEncoderDecoderModel

tokenizer = AutoTokenizer.from_pretrained("dumperize/movie-picture-captioning")
feature_extractor = ViTFeatureExtractor.from_pretrained(
    "dumperize/movie-picture-captioning")
model = VisionEncoderDecoderModel.from_pretrained(
    "dumperize/movie-picture-captioning")

max_length = 128
num_beams = 4
gen_kwargs = {"max_length": max_length, "num_beams": num_beams}

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

image_path = 'data/img_example/1.jpeg'
image = Image.open(image_path)
image = image.resize((224, 224))
if image.mode != "RGB":
    image = image.convert(mode="RGB")

pixel_values = feature_extractor(
    images=[image], return_tensors="pt").pixel_values
pixel_values = pixel_values.to(device)

output_ids = model.generate(pixel_values, **gen_kwargs)

preds = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
print([pred.strip() for pred in preds])
