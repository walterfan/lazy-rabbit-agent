from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
import os, sys
import argparse
from dotenv import load_dotenv
from llm_token_util import create_message_trimmer
load_dotenv()

class LazyLlmAgent:
    def __init__(self, system_prompt, session_id="default", max_tokens=4096):

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
        self.with_message_history = self._setup_message_history()
        self.config = {"configurable": {"session_id": self.session_id}}
    
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
        return ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

    def get_session_history(self, session_id):
        """Get or create a session history for the given session ID"""
        if session_id not in self.store:
            self.store[session_id] = InMemoryChatMessageHistory()
        return self.store[session_id]
    
    def _setup_message_history(self):
        """Set up the runnable with message history"""
        return RunnableWithMessageHistory(
            self.trimmer | self.prompt | self.chat_model,
            self.get_session_history
        )
    
    def process_input(self, user_input):
        """Process a single user input and return the response"""
        stream = self.with_message_history.stream(
            {"messages": [HumanMessage(content=user_input)]},
            config=self.config
        )
        
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
            self.process_input(user_input)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LazyLlmAgent - A conversational AI agent")
    parser.add_argument("--system-prompt", type=str, default="你现在扮演孔子的角色，尽量按照孔子的风格回复，不要出现'子曰'", help="System prompt for the agent")
    parser.add_argument("--session-id", type=str, default="waltertest", help="Session ID for conversation history")
    
    args = parser.parse_args()

    agent = LazyLlmAgent(
        system_prompt=args.system_prompt,
        session_id=args.session_id
    )

    agent.run_interactive()
