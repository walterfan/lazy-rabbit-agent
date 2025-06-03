# Lazy Rabbit Agent

It's an experimental project to build a LLM Agent that interact with LLM and local knowledge base.

Still building...

## Design

Tech Stack: Vue.js + FastAPI + Langchain

## Deployment

```shell
cp .env.example ./deploy/.env
cd deploy
docker-compose up -d

```

## Documents

* [如何通过知识图谱做大语言模型的 RAG](doc/graph_rag.md)
* [集成大语言模型的应用](doc/llm_integration.md)
* [Langchain 简介](doc/langchain_overview.md)
* [Langchain 快速开始](doc/langchain_overview.md)

## Examples

* [Simple LLM Agent](example/simple_llm_agent.py): 一个简单的 LLM Client 的封装
* [langchina demo 1](example/langchain_demo_1.py): 演示如何利用 langchain 做自然语言文本的结构化分析
* [langchina demo 2](example/langchain_demo_2.py): 演示如何利用 langchain 及其 WebBaseLoader 分析博客文章
* [langchina server](example/langchain_demo_2.py): 演示如何使用 FastAPI 来暴露 langchain API
* [LLM FIM example](example/llm_fim_exam.py): 演示 LLM 的 FIM (Fill In the Middle) 功能
* [LLM Function Call example](example/llm_function_call.py): 演示 LLM 的 Function Call 功能


## Glossaries

* GPT: Generative Pre-trained Transformer
* RAG: Retrieval-Augmented Generation
* LCEL: LangChain Expression Language


## Setup env

### Create DB and environment file
* create datbase

```sql

CREATE DATABASE IF NOT EXISTS lra;

CREATE USER IF NOT EXISTS 'your_username'@'%' IDENTIFIED BY 'your_password';

GRANT ALL PRIVILEGES ON lra.* TO 'your_username'@'%';

FLUSH PRIVILEGES;
```

## Install dependencies

```shell
 1554  pip install langchain unstructured openai
 1558  pip install pdfminer.six --upgrade
 1560  pip install pillow-heif\n
 1561  pip install --upgrade Pillow\n
 1564  brew install libheif
 ```

## Components

### Local Knowledge base

* DB: Relational or Graph database
* Documents: PDF, PPT, WORD, etc.
* Wiki
* ...

### Backend

based on FastAPI and langchain


### Frontend

based on vue.js 3 and element plus UI framework


