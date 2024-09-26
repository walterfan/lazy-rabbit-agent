import PyPDF2
from langchain_community.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from loguru import logger
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

import os, sys
load_dotenv()
logger.add(sys.stdout,
           format="{time} {message}",
           filter="client",
           level="DEBUG")

def extract_text_from_pdf(file_path):
    reader = PyPDF2.PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

pdf_text = extract_text_from_pdf("gst-dynamic-pipeline.pdf")
print(f"PDF content={pdf_text}")
print("-"*80)
# 创建 LLM 对象 (使用 OpenAI GPT)
llm = ChatOpenAI(
    model='deepseek-chat',
    openai_api_key=os.getenv("DS_LLM_API_KEY"),
    openai_api_base=os.getenv("DS_LLM_BASE_URL"),
    max_tokens=1024
)
# 定义总结的 Prompt
prompt_template = """
请总结以下内容：
{pdf_text}
总结：
"""

pdf_prompt = PromptTemplate(
    input_variables=["pdf_text"],
    template=prompt_template,
)

# 创建 LLMChain
chain = pdf_prompt | llm

# 使用 LLM 生成总结
summary = chain.invoke({"pdf_text", pdf_text})
print("PDF summary: \n", summary.content)
