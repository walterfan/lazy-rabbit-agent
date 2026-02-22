# Langchain Quick Start

三大要素

1. 模型 文本生成模型或者对话模型(ChatModel)
2. 输入 Prompt Temmplate
3. 输出 Output Parser

利用 LangChain 开发一个将医生说的自然语言解析成结构化 JSON 的工具，可以遵循以下步骤。这包括使用 LangChain 框架来处理自然语言，并生成对应的结构化数据。

## 解析医生说话的实例

### 步骤 1: 安装必要的依赖
首先，确保安装了必要的 Python 包：
```bash
pip install langchain openai
```

### 步骤 2: 设置 OpenAI API 密钥
LangChain 可以使用 OpenAI 的 GPT 模型进行自然语言处理。在代码中设置你的 OpenAI API 密钥：
```python
import os
from langchain.llms import OpenAI

os.environ["OPENAI_API_KEY"] = "your-openai-api-key"
```

### 步骤 3: 定义目标 JSON 结构
确定医生自然语言需要映射到的 JSON 结构。例如，如果你想提取患者信息，结构可能如下：
```json
{
    "patient_name": "",
    "age": "",
    "symptoms": [],
    "diagnosis": "",
    "treatment_plan": ""
}
```

### 步骤 4: 设计提示（Prompt）
为了将医生的自然语言解析成上述 JSON 结构，你需要设计一个提示。这段提示会引导模型生成符合你期望的 JSON 格式。例如：
```python
prompt_template = """
将以下医生的描述转换成JSON格式：

描述: "{description}"

JSON格式:
{{
    "patient_name": "",
    "age": "",
    "symptoms": [],
    "diagnosis": "",
    "treatment_plan": ""
}}
"""
```

### 步骤 5: 构建 LangChain 管道
使用 LangChain 创建一个简单的链式调用来生成 JSON：

```python
from typing import List
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import BaseOutputParser

import pprint
import os, sys
import json
from loguru import logger
from dotenv import load_dotenv

load_dotenv()
logger.add(sys.stdout,
           format="{time} {message}",
           filter="client",
           level="DEBUG")

llm = ChatOpenAI(
    model='deepseek-chat',
    openai_api_key=os.getenv("DS_LLM_API_KEY"),
    openai_api_base=os.getenv("DS_LLM_BASE_URL"),
    max_tokens=4096
)


class JsonOutputParser(BaseOutputParser[dict]):
    def parse(self, text: str) -> List[str]:
        text = text.lstrip("```json").rstrip("```")
        return json.loads(text)


system_template = """你是一个能解释医生说话内容的助手, 当医生输入一段话, 你会解析其内容将它转换成 JSON 格式"""

human_template = """
将以下医生的描述转换成JSON格式：

描述: "{text}"

JSON格式:
{{
    "patient_name": "",
    "age": "",
    "symptoms": [],
    "diagnosis": "",
    "treatment_plan": ""
}}
"""

chat_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_template),
        ("human", human_template)
     ]
)

if __name__ == "__main__":
    chain = chat_prompt | llm | JsonOutputParser()
    user_prompt = "患者名叫李雷，35岁，出现了发烧和咳嗽的症状。诊断为急性支气管炎，建议服用抗生素并多喝水。"
    result = chain.invoke({"text", user_prompt})
    pprint.pprint(result)
```

### 步骤 6: 优化与扩展
你可以根据需求扩展和优化解析能力：
- **添加更多的字段**：例如，添加更多患者细节或诊断信息。
- **增强提示**：通过调整提示的内容和格式，提高生成的 JSON 准确性。
- **集成语音识别**：将语音转文本模块集成到此管道中，使医生的口述自动转换成文本，再进行解析。

### 步骤 7: 部署与测试
最后，将此工具集成到你的应用中，例如一个Web应用或移动应用中，并通过实际使用场景进行测试和优化。

### 示例输出
运行 `python langchain_demo_1.py`

假设输入描述为：患者名叫李雷，35岁，出现了发烧和咳嗽的症状。诊断为急性支气管炎，建议服用抗生素并多喝水。
我们所得到的输出如下

```python

{'age': 35,
 'diagnosis': '急性支气管炎',
 'patient_name': '李雷',
 'symptoms': ['发烧', '咳嗽'],
 'treatment_plan': '服用抗生素并多喝水'}
```

通过LangChain，你可以快速构建这种应用，并根据实际需求进一步优化生成的JSON结构。