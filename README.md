# LLM Agent

It's an experimental project to build a LLM Agent that interact with LLM and local knowledge base.



## Deployment

```shell
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

## Components

### Local Knowledge base

* DB: Relational or Graph database
* Documents: PDF, PPT, WORD, etc.
* Wiki
* ...

### Backend based on FastAPI and langchain

```

backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── users.py
│   │   │   │   ├── items.py
│   │   │   └── __init__.py
│   │   ├── dependencies/
│   │   │   ├── __init__.py
│   │   │   ├── authentication.py
│   │   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── security.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── item.py
│   │   ├── session.py
│   ├── main.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── item.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── user_service.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_users.py
│   │   ├── test_items.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── utils.py
│   └── __init__.py
├── .env
├── alembic.ini
├── README.md
├── requirements.txt
├── Dockerfile
└── docker-compose.yml

```

### Frontend based on VUE3

```
frontend/
├── public/
│   ├── index.html
│   ├── favicon.ico
├── src/
│   ├── assets/
│   │   ├── logo.png
│   ├── components/
│   │   ├── BaseButton.vue
│   │   ├── BaseInput.vue
│   ├── composables/
│   │   ├── useFetchData.js
│   ├── directives/
│   │   ├── vFocus.js
│   ├── layouts/
│   │   ├── DefaultLayout.vue
│   │   ├── AuthLayout.vue
│   ├── pages/
│   │   ├── Home.vue
│   │   ├── About.vue
│   │   ├── Login.vue
│   ├── router/
│   │   ├── index.js
│   ├── store/
│   │   ├── index.js
│   ├── styles/
│   │   ├── main.css
│   │   ├── variables.scss
│   ├── utils/
│   │   ├── dateFormatter.js
│   ├── views/
│   │   ├── Dashboard.vue
│   │   ├── Profile.vue
│   ├── App.vue
│   ├── main.js
├── tests/
│   ├── unit/
│   │   ├── example.spec.js
│   ├── e2e/
│   │   ├── example.spec.js
├── .env
├── .eslintrc.js
├── .gitignore
├── babel.config.js
├── package.json
├── README.md
├── vue.config.js

```