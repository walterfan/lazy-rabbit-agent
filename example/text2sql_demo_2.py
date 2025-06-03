from typing import Optional, Dict
from pydantic import BaseModel
from langchain_community.chat_models import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain.text_splitter import CharacterTextSplitter
from sqlalchemy import create_engine, inspect
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
import sqlite3
import json
import argparse
import httpx
import os
import re
from loguru import logger
import warnings
import urllib3
from urllib3.exceptions import InsecureRequestWarning
import ssl
from dotenv import load_dotenv

load_dotenv()

class QueryRequest(BaseModel):
    session_id: str
    query: str

class SQLResponse(BaseModel):
    sql: str
    mybatis: str

class Text2SQLGenerator:
    def __init__(self):
        self._setup_environment()
        self._initialize_components()
        
    def _setup_environment(self):
        """Configure environment settings and warnings"""
        warnings.filterwarnings('ignore', category=InsecureRequestWarning)
        urllib3.disable_warnings(InsecureRequestWarning)
        os.environ.update({
            "PYTHONHTTPSVERIFY": "0",
            "REQUESTS_CA_BUNDLE": "",
            "SSL_CERT_FILE": ""
        })
        ssl._create_default_https_context = ssl._create_unverified_context
        self._patch_httpx()

    def _patch_httpx(self):
        """Patch httpx to disable SSL verification"""
        original_init = httpx.Client.__init__
        def patched_init(self, *args, **kwargs):
            kwargs['verify'] = False
            original_init(self, *args, **kwargs)
        httpx.Client.__init__ = patched_init

    def _initialize_components(self):
        """Initialize all required components"""
        self.embedding = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
        self.llm = self._create_llm()
        self.sqlite_conn = sqlite3.connect("conversation.db", check_same_thread=False)
        self._initialize_database()
        self.text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        self.PERSIST_DIRECTORY = "chroma_store"
        
    def _create_llm(self) -> ChatOpenAI:
        """Create and configure the LLM instance"""
        return ChatOpenAI(
            model=os.getenv("LLM_MODEL"),
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL"),
            temperature=float(os.getenv("LLM_TEMPERATURE", 0.5)),
            callbacks=None,
            verbose=True,
        )

    def _initialize_database(self):
        """Initialize the SQLite database"""
        self.sqlite_conn.execute('''CREATE TABLE IF NOT EXISTS conversation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            user_query TEXT NOT NULL,
            llm_prompt TEXT NOT NULL,
            llm_response TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')

    def _get_mysql_schema(self, mysql_url: str) -> str:
        """Extract schema from MySQL database"""
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

    def _build_vector_store(self, schema_text: str) -> Chroma:
        """Build and persist vector store from schema"""
        docs = self.text_splitter.create_documents([schema_text])
        return Chroma.from_documents(
            docs,
            self.embedding,
            collection_name="schema",
            persist_directory=self.PERSIST_DIRECTORY
        )

    def _get_vector_store(self, mysql_url: str) -> Chroma:
        """Get existing or create new vector store"""
        if not os.path.exists(self.PERSIST_DIRECTORY):
            os.makedirs(self.PERSIST_DIRECTORY)
            schema = self._get_mysql_schema(mysql_url)
            vectorstore = self._build_vector_store(schema)
            vectorstore.persist()
            return vectorstore
        return Chroma(
            collection_name="schema",
            embedding_function=self.embedding,
            persist_directory=self.PERSIST_DIRECTORY
        )

    @staticmethod
    def _extract_json(content: str) -> Dict:
        """Extract JSON from LLM response with fallback"""
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
        
        match = re.search(r'```json\n?(.*?)\n?```', content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except json.JSONDecodeError:
                pass
        
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        
        raise ValueError(f"No valid JSON found in response: {content}")

    def generate_sql(self, request: QueryRequest) -> SQLResponse:
        """Main method to generate SQL from natural language query"""
        mysql_url = os.getenv("MYSQL_URL")

        if not mysql_url:
            mysql_url = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

        
        logger.info(f"Connecting to MySQL at {mysql_url}")
        vectorstore = self._get_vector_store(mysql_url)
        retriever = vectorstore.as_retriever()

        history = self._get_conversation_history(request.session_id)
        docs = retriever.get_relevant_documents(request.query)
        context = "\n---\n".join(doc.page_content for doc in docs)

        prompt = self._build_prompt(history, context, request.query)
        logger.info(f"Generated prompt: {prompt}")
        
        result_msg = self.llm.invoke(prompt)
        logger.info(f"LLM result: {result_msg.text()}")
        
        result_json = self._extract_json(result_msg.content)
        self._save_conversation(request, prompt, result_msg.content)
        
        return SQLResponse(
            sql=result_json.get("sql", ""),
            mybatis=result_json.get("mybatis", "")
        )

    def _get_conversation_history(self, session_id: str) -> str:
        """Retrieve conversation history for the session"""
        history = ""
        rows = self.sqlite_conn.execute(
            "SELECT user_query, llm_response FROM conversation WHERE session_id = ? ORDER BY timestamp",
            (session_id,)
        )
        for q, r in rows.fetchall():
            history += f"User: {q}\nSQL: {r}\n\n"
        return history

    def _build_prompt(self, history: str, context: str, question: str) -> str:
        """Construct the prompt for LLM"""
        response_schemas = [
            ResponseSchema(name="sql", description="Generated SQL query"),
            ResponseSchema(name="mybatis", description="MyBatis XML mapper")
        ]
        output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
        
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
        return prompt_template.format(history=history, context=context, question=question)

    def _save_conversation(self, request: QueryRequest, prompt: str, response: str):
        """Save conversation to database"""
        self.sqlite_conn.execute(
            "INSERT INTO conversation (session_id, user_query, llm_prompt, llm_response) VALUES (?, ?, ?, ?)",
            (request.session_id, request.query, prompt, response)
        )
        self.sqlite_conn.commit()

    def __del__(self):
        """Cleanup when instance is destroyed"""
        if hasattr(self, 'sqlite_conn'):
            self.sqlite_conn.close()




if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Generate SQL from natural language queries")
    parser.add_argument(
        "--session-id",
        type=str,
        default="default_session",
        help="Session ID for conversation history (default: 'default_session')"
    )
    parser.add_argument(
        "query",
        type=str,
        help="Natural language query to convert to SQL"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    # Parse arguments
    args = parser.parse_args()

    # Initialize generator and process query
    generator = Text2SQLGenerator()
    request = QueryRequest(session_id=args.session_id, query=args.query)
    
    try:
        response = generator.generate_sql(request)
        print("\nResults:")
        print(f"SQL: {response.sql}")
        print(f"MyBatis: {response.mybatis}")
    except Exception as e:
        if args.verbose:
            logger.error(f"Error: {e}")
        else:
            print(f"Error: {str(e)}")
        exit(1)