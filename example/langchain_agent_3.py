from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import HumanMessage
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import TextLoader
from operator import itemgetter
from typing import List
import os, sys
import argparse
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from llm_token_util import create_message_trimmer
from rag_util import create_retriever, create_vector_store, load_document_to_vector_store
load_dotenv()

class LazyLlmAgent:
    def __init__(self, system_prompt, session_id="default", max_tokens=4096):

        os.environ["OPENAI_API_KEY"] = os.getenv("LLM_API_KEY")
        os.environ["USER_AGENT"] = "waltertest"

        self.model_name = os.getenv("LLM_MODEL")
        self.api_key = os.getenv("LLM_API_KEY")
        self.api_base = os.getenv("LLM_BASE_URL")

        self.max_tokens = max_tokens
        self.system_prompt = system_prompt
        self.session_id = session_id
        self.store = {}
        
        # Initialize components
        self.chat_model = self._setup_chat_model()
        self.prompt = self._setup_prompt()
        self.trimmer = create_message_trimmer()
        self.vector_store = create_vector_store()
        self.retriever = create_retriever(self.vector_store)
        self.with_message_history = self._setup_message_history()
        self.config = {"configurable": {"session_id": self.session_id}}


    def load_document(self, file_path):
        load_document_to_vector_store(file_path, self.vector_store)
        print(f"load {file_path} to vector store success")

    def _setup_chat_model(self):
        """Initialize the chat model"""
        return ChatOpenAI(
            model=self.model_name,
            openai_api_key=self.api_key,
            openai_api_base=self.api_base,
            max_tokens=self.max_tokens
        )
    
    def _setup_prompt(self):
        """Set up the chat prompt template"""

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are an assistant for question-answering tasks.
                    Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know.
                    Context: {context}""",
                ),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{question}"),
            ]
        )
        return prompt
    def format_docs(self,docs):
        return "\n\n".join(doc.page_content for doc in docs)
    def get_session_history(self, session_id):
        """Get or create a session history for the given session ID"""
        if session_id not in self.store:
            self.store[session_id] = InMemoryChatMessageHistory()
        return self.store[session_id]

    def _setup_message_history(self):
        context = itemgetter("question") | self.retriever | self.format_docs
        first_step = RunnablePassthrough.assign(context=context)
        chain = first_step | self.prompt | self.trimmer | self.chat_model

        with_message_history = RunnableWithMessageHistory(
            chain,
            self.get_session_history,
            input_messages_key="question",
            history_messages_key="history",)
        return with_message_history
    
    def process_input(self, user_input):
        """Process a single user input and return the response"""

        stream = self.with_message_history.stream(
            {"question": user_input},
            config=self.config )

        response = ""
        for chunk in stream:
            content = chunk.content
            print(content, end='', flush=True)
            response += content
        print()
        return response
    
    def run_interactive(self):
        """Run the agent in interactive mode"""
        print(f"Starting interactive session with ID: {self.session_id}")
        print(f"Type 'exit' to end the session")
        
        while True:
            user_input = input("You:> ")
            if user_input.lower() == 'exit':
                break
            if user_input == "":
                continue
            self.process_input(user_input)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LazyLlmAgent - A conversational AI agent")
    parser.add_argument('-r', "--role", type=str, default="你现在扮演孔子的角色，尽量按照孔子的风格回复，不要出现'子曰'", help="System prompt for the agent")
    parser.add_argument("-s", "--session", type=str, default="waltertest", help="Session ID for conversation history")
    parser.add_argument('-f', "--file", type=str, default="analects.txt", help="file path")

    args = parser.parse_args()

    agent = LazyLlmAgent(
        system_prompt=args.role,
        session_id=args.session
    )
    agent.load_document(args.file)
    agent.run_interactive()
