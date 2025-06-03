from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
#from langchain.chat_models import ChatOpenAI
from langchain_community.chat_models import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain.text_splitter import CharacterTextSplitter
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv
import sqlite3
import json
import uvicorn
import os
from openai import OpenAI
from loguru  import logger
import ssl
import simple_llm_agent
# Create unverified context
ssl._create_default_https_context = ssl._create_unverified_context
# --------------------------- Load environment variables ---------------------------
load_dotenv()

app = FastAPI()

# --------------------------- Models ---------------------------
class QueryRequest(BaseModel):
    session_id: str
    query: str

class SQLResponse(BaseModel):
    sql: str
    mybatis: str

# --------------------------- DB Schema Extraction ---------------------------
def get_mysql_schema(mysql_url: str) -> str:
    engine = create_engine(mysql_url)
    inspector = inspect(engine)
    schema_text = ""
    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)
        schema_text += f"CREATE TABLE {table_name} (\n"
        col_defs = [f"  {col['name']} {col['type']}" for col in columns]
        schema_text += ",\n".join(col_defs)
        schema_text += "\n);\n\n"
    return schema_text

# --------------------------- LangChain Setup ---------------------------
embedding = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")

from langchain_core.utils.function_calling import convert_to_openai_tool
"""
client = OpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL"),
    timeout=30.0,
    http_client=httpx.Client(verify=False),
)

llm = ChatOpenAI(
    model=os.getenv("LLM_MODEL"),
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL"),
    temperature=float(os.getenv("LLM_TEMPERATURE", 0.5)),
    callbacks=None,
    verbose=True,
    client=client,
)
# got error opeai no create(), it should be a version issue
"""
agent = simple_llm_agent.LlmAgent(api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL"),
            model=os.getenv("LLM_MODEL"))

sqlite_conn = sqlite3.connect("conversation.db", check_same_thread=False)
sqlite_conn.execute('''CREATE TABLE IF NOT EXISTS conversation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    user_query TEXT NOT NULL,
    llm_prompt TEXT NOT NULL,
    llm_response TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)''')

text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

# --------------------------- Vector Store Build ---------------------------
PERSIST_DIRECTORY = "chroma_store"

def build_vector_store(schema_text: str):
    docs = text_splitter.create_documents([schema_text])
    return Chroma.from_documents(
        docs,
        embedding,
        collection_name="schema",
        persist_directory=PERSIST_DIRECTORY
    )

# --------------------------- API Endpoint ---------------------------
@app.post("/text2sql", response_model=SQLResponse)
def text2sql(req: QueryRequest):
    mysql_url=f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

    if not mysql_url:
        raise HTTPException(status_code=500, detail="MYSQL_URL not set")
    logger.info(f"Connecting to MySQL at {mysql_url}")
    if not os.path.exists(PERSIST_DIRECTORY):
        os.makedirs(PERSIST_DIRECTORY)
        schema = get_mysql_schema(mysql_url)
        vectorstore = build_vector_store(schema)
        vectorstore.persist()
    else:
        vectorstore = Chroma(
            collection_name="schema",
            embedding_function=embedding,
            persist_directory=PERSIST_DIRECTORY
        )

    retriever = vectorstore.as_retriever()

    history = ""
    rows = sqlite_conn.execute("SELECT user_query, llm_response FROM conversation WHERE session_id = ? ORDER BY timestamp", (req.session_id,))
    for q, r in rows.fetchall():
        history += f"User: {q}\nSQL: {r}\n\n"

    prompt_template = PromptTemplate.from_template("""
Previous conversation:
{history}

Database Schema:
{context}

Now generate SQL and the corresponding MyBatis XML mapper for:
{question}

Respond in JSON format:
{{"sql": "...", "mybatis": "..."}}
""")

    docs = retriever.get_relevant_documents(req.query)
    context = "\n---\n".join(doc.page_content for doc in docs)

    prompt = prompt_template.format(history=history, context=context, question=req.query)
    logger.info(f"Generated prompt: {prompt}")
    #result_text = llm.invoke(prompt)
    result_text = agent.get_json_response(system_prompt="You are a SQL generator", user_prompt=prompt)


    try:
        result_json = json.loads(result_text)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="LLM response is not valid JSON")

    sqlite_conn.execute("INSERT INTO conversation (session_id, user_query, llm_prompt, llm_response) VALUES (?, ?, ?, ?)",
                        (req.session_id, req.query, prompt, result_text))
    sqlite_conn.commit()

    return SQLResponse(sql=result_json.get("sql", ""), mybatis=result_json.get("mybatis", ""))

# --------------------------- Main Entry ---------------------------
if __name__ == "__main__":
    logger.info("Starting Text2SQL service at port 8003...")
    uvicorn.run("text2sql_demo:app", host="0.0.0.0", port=8003, reload=True)