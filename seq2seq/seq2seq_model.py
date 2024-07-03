from transformers import BertTokenizer, BartForConditionalGeneration
import torch
from torch.utils.data import DataLoader, Dataset, random_split
from tqdm import tqdm
import json
import os
from rouge import Rouge
from sacrebleu import corpus_bleu

# 指向您存放模型文件的本地目录
local_model_directory = r'D:\pythonProject\seq2seq\bart-base-chinense'

# 从本地文件加载模型和分词器
tokenizer = BertTokenizer.from_pretrained(local_model_directory)
model = BartForConditionalGeneration.from_pretrained(local_model_directory)

# 数据文件路径
# data_file_path = r'D:\毕业设计\用药推荐\json\data\modified_processed_patients.json'

# 数据文件路径
train_data_file_path = r'D:\pythonProject\seq2seq\result041(2)(1).json'
test_data_file_path = r'D:\pythonProject\seq2seq\test.json'
validation_data_file_path = r'D:\pythonProject\seq2seq\val.json'


class CustomDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: val[idx].clone().detach() for key, val in self.encodings.items()}
        # item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = self.labels['input_ids'][idx].clone().detach()
        return item

    def __len__(self):
        return len(self.labels['input_ids'])


def load_and_process_data(file_path, num_samples=None):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        if num_samples:
            data = data[:num_samples]
    processed_data = []
    for item in data:
        input_text = item["Input"]
        target_text = item["Output"]
        processed_data.append((input_text, target_text))
    return processed_data


def prepare_dataset(data_file_path, num_samples=None):
    # 将num_samples参数传递给load_and_process_data函数
    data = load_and_process_data(data_file_path, num_samples=num_samples)
    inputs = tokenizer([x[0] for x in data], padding=True, truncation=True, return_tensors="pt", max_length=512)
    targets = tokenizer([x[1] for x in data], padding=True, truncation=True, return_tensors="pt", max_length=512)
    dataset = CustomDataset(inputs, targets)
    return dataset


num_samples = None
# 准备数据集
train_dataset = prepare_dataset(train_data_file_path, num_samples=num_samples)
val_dataset = prepare_dataset(validation_data_file_path, num_samples=num_samples)
test_dataset = prepare_dataset(test_data_file_path, num_samples=num_samples)

# 数据加载器
train_loader = DataLoader(train_dataset, batch_size=8, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=4, shuffle=False)
test_loader = DataLoader(test_dataset, batch_size=4, shuffle=False)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

optimizer = torch.optim.Adam(model.parameters(), lr=5e-5)

epochs = 20 # 实际应用中可能需要更多的epoch

results = {}  # 初始化结果字典

# 训练和验证
for epoch in range(epochs):
    model.train()
    total_loss = 0
    for batch in tqdm(train_loader, desc=f"Training Epoch {epoch + 1}"):
        optimizer.zero_grad()
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['labels'].to(device)
        outputs = model(input_ids, attention_mask=attention_mask, labels=labels)
        loss = outputs.loss
        loss.backward()
        optimizer.step()
        total_loss += loss.item()

    # 验证损失
    model.eval()
    total_eval_loss = 0
    for batch in tqdm(val_loader, desc=f"Validating Epoch {epoch + 1}"):
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['labels'].to(device)
        with torch.no_grad():
            outputs = model(input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss
            total_eval_loss += loss.item()

    print(
        f"Epoch: {epoch}, Training Loss: {total_loss / len(train_loader)}, Validation Loss: {total_eval_loss / len(val_loader)}")

    # 更新结果字典
    results[f"epoch_{epoch + 1}"] = {
        "train_loss": total_loss / len(train_loader),
        "val_loss": total_eval_loss / len(val_loader),
    }

# 测试集评估和计算BLEU和ROUGE指标
model.eval()
predictions = []
references = []
with torch.no_grad():
    for batch in tqdm(test_loader, desc="Evaluating on Test Set"):
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['labels'].to(device)

        # 生成预测结果
        outputs = model.generate(input_ids, attention_mask=attention_mask, max_new_tokens=50)

        # 解码文本
        pred_text = [tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=True) for g in outputs]
        labels_text = [tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=True) for g in labels]

        predictions.extend(pred_text)
        references.extend(labels_text)

# 清理空的预测和参考文本
cleaned_predictions = []
cleaned_references = []
for pred, ref in zip(predictions, references):
    if pred.strip() and ref.strip():  # 确保预测和参考都不是空字符串
        cleaned_predictions.append(pred)
        cleaned_references.append(ref)

# 检查清理后的数据
if not cleaned_predictions or not cleaned_references:
    print("警告：清理后没有有效的预测或参考文本可用于评估。")
else:
    # 计算BLEU和ROUGE
    bleu_score = corpus_bleu(cleaned_predictions, [cleaned_references]).score
    rouge = Rouge()
    rouge_scores = rouge.get_scores(cleaned_predictions, cleaned_references, avg=True)

    print(f"BLEU score: {bleu_score}")
    print(f"ROUGE scores: {rouge_scores}")

    # 将评估结果添加到结果字典中
    results['bleu'] = bleu_score
    results['rouge'] = rouge_scores

    # 保存模型参数和结果
    if not os.path.exists('results'):
        os.makedirs('results')
    with open('results/results.json', 'w') as f:
        json.dump(results, f)

    # 保存模型
    model.save_pretrained("./my_finetuned_bart-large-chinese-model_2_for20")

# # 计算BLEU和ROUGE
# cc = SmoothingFunction()
# # bleu_score = corpus_bleu([[ref.split()] for ref in references], [pred.split() for pred in predictions])
# # bleu_score = corpus_bleu([[ref.split()] for ref in references], [pred.split() for pred in predictions], smoothing_function=cc.method4)
# bleu_score = corpus_bleu(predictions, [references]).score
# rouge = Rouge()
# rouge_scores = rouge.get_scores(predictions, references, avg=True)
#
# print(f"BLEU score: {bleu_score}")
# print(f"ROUGE scores: {rouge_scores}")
#
# # 将评估结果添加到结果字典中
# results['bleu'] = bleu_score
# results['rouge'] = rouge_scores
#
# # 保存模型参数和结果
# if not os.path.exists('results'):
#     os.makedirs('results')
# with open('results/results.json', 'w') as f:
#     json.dump(results, f)
#
# # 保存模型
# model.save_pretrained("./my_finetuned_bart_model")
