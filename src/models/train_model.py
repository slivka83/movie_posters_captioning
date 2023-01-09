from PIL import Image
from torch.utils.data import Dataset
import torch
import pandas as pd
from transformers import ViTFeatureExtractor, BertTokenizer, VisionEncoderDecoderModel
from transformers import VisionEncoderDecoderModel
from transformers import default_data_collator
from transformers import Seq2SeqTrainer, Seq2SeqTrainingArguments
from datasets import load_metric


global_path = '/Users/user/Documents/vscode/movie_posters_captioning/'
train_path = global_path + 'data/interim/train.csv'
val_path = global_path + 'data/interim/val.csv'

train_df = pd.read_csv(train_path)
test_df = pd.read_csv(val_path)

train_df = train_df[train_df['nameRu'].notna()]
test_df = test_df[test_df['nameRu'].notna()]


train_df.reset_index(drop=True, inplace=True)
test_df.reset_index(drop=True, inplace=True)


class IAMDataset(Dataset):
    def __init__(self, root_dir, df, feature_extractor, tokenizer, max_target_length=10):
        self.root_dir = root_dir
        self.df = df
        # self.processor = processor #feature_extractor
        self.tokenizer = tokenizer
        self.feature_extractor = feature_extractor
        self.max_target_length = max_target_length

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        # get file name + text
        file_name = str(self.df['filmId'][idx]) + '.jpg'
        text = self.df['nameRu'][idx]
        # prepare image (i.e. resize + normalize)
        image = Image.open(self.root_dir + file_name).convert("RGB")
        image = image.resize((224, 224))
        pixel_values = self.feature_extractor(
            image, return_tensors="pt").pixel_values
        # add labels (input_ids) by encoding the text

        labels = self.tokenizer(text,
                                truncation='longest_first',
                                padding="max_length",
                                # return_tensors="pt",
                                max_length=self.max_target_length).input_ids
        # important: make sure that PAD tokens are ignored by the loss function
        labels = [label if label !=
                  self.tokenizer.pad_token_id else -100 for label in labels]
        encoding = {"pixel_values": pixel_values.squeeze(),
                    "labels": torch.tensor(labels)}
        return encoding


model = VisionEncoderDecoderModel.from_encoder_decoder_pretrained(
    "google/vit-base-patch16-224-in21k", "DeepPavlov/rubert-base-cased"
)

feature_extractor = ViTFeatureExtractor.from_pretrained(
    "google/vit-base-patch16-224-in21k")
tokenizer = BertTokenizer.from_pretrained("DeepPavlov/rubert-base-cased")

for param in model.encoder.parameters():
    param.requires_grad = False

train_dataset = IAMDataset(root_dir=global_path + 'data/img/',
                           df=train_df[:100],
                           feature_extractor=feature_extractor,
                           tokenizer=tokenizer
                           )
eval_dataset = IAMDataset(root_dir=global_path + 'data/img/',
                          df=test_df[:30],
                          feature_extractor=feature_extractor,
                          tokenizer=tokenizer
                          )
print("Number of training examples:", len(train_dataset))
print("Number of validation examples:", len(eval_dataset))


for param in model.base_model.encoder.parameters():
    param.requires_grad = False
# set special tokens used for creating the decoder_input_ids from the labels
model.config.decoder_start_token_id = tokenizer.cls_token_id
model.config.pad_token_id = tokenizer.pad_token_id
# make sure vocab size is set correctly
model.config.vocab_size = model.config.decoder.vocab_size

# set beam search parameters
model.config.eos_token_id = tokenizer.sep_token_id
model.config.max_length = 10
model.config.early_stopping = True
model.config.no_repeat_ngram_size = 2
model.config.length_penalty = 2.0
model.config.num_beams = 4

training_args = Seq2SeqTrainingArguments(
    # num_train_epochs=3,
    predict_with_generate=True,
    # evaluation_strategy="steps",
    per_device_train_batch_size=6,
    per_device_eval_batch_size=6,
    fp16=True,
    output_dir="./",
    logging_steps=2,
    save_steps=500,
    eval_steps=10,
)

metric = load_metric('sacrebleu')


def compute_metrics(pred):
    labels_ids = pred.label_ids
    pred_ids = pred.predictions

    pred_str = tokenizer.batch_decode(pred_ids, skip_special_tokens=True)
    labels_ids[labels_ids == -100] = tokenizer.pad_token_id
    label_str = tokenizer.batch_decode(labels_ids, skip_special_tokens=True)

    bleu = metric.compute(predictions=[pred_str], references=[label_str])

    return {"bleu": bleu}


# instantiate trainer
trainer = Seq2SeqTrainer(
    model=model,
    tokenizer=feature_extractor,
    args=training_args,
    compute_metrics=compute_metrics,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    data_collator=default_data_collator,
)
trainer.train()

#  check result
max_length = 16
num_beams = 4
gen_kwargs = {"max_length": max_length, "num_beams": num_beams}

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

images = []
image_path = global_path + 'data/img/299.jpg'
i_image = Image.open(image_path)
i_image = i_image.resize((224, 224))
if i_image.mode != "RGB":
    i_image = i_image.convert(mode="RGB")

# model.feat
images.append(i_image)
pixel_values = feature_extractor(
    images=images, return_tensors="pt").pixel_values
pixel_values = pixel_values.to(device)

output_ids = model.generate(pixel_values, **gen_kwargs)

preds = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
preds = [pred.strip() for pred in preds]
print(preds)
