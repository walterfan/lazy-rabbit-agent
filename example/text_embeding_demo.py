#!/usr/bin/env python3
from transformers import AutoTokenizer, AutoModel
import torch

# 使用 Hugging Face 提供的预训练模型
model_name = "sentence-transformers/all-MiniLM-L6-v2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

# 转换文本为向量
def text_to_embedding(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
        # 获取句子嵌入（通常是最后一层的平均池化）
        embeddings = outputs.last_hidden_state.mean(dim=1).squeeze()
    return embeddings.numpy()

# 测试
text = "This is a sample sentence."
embedding = text_to_embedding(text)
print(embedding)