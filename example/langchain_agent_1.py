from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
import os, sys
from dotenv import load_dotenv

load_dotenv()


#os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["OPENAI_API_KEY"] = os.getenv("LLM_API_KEY")
os.environ["USER_AGENT"] = "waltertest"

chat_model = ChatOpenAI(
    model='deepseek-chat',
    openai_api_key=os.getenv("LLM_API_KEY"),
    openai_api_base=os.getenv("LLM_BASE_URL"),
    max_tokens=4096
)

store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "你现在扮演孔子的角色，尽量按照孔子的风格回复，不要出现‘子曰’",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

with_message_history = RunnableWithMessageHistory(
    prompt | chat_model,
    get_session_history
)

config = {"configurable": {"session_id": "dreamhead"}}


while True:
    user_input = input("You:> ")
    if user_input.lower() == 'exit':
        break
    stream = with_message_history.stream(
        {"messages": [HumanMessage(content=user_input)]},
        config=config
    )
    for chunk in stream:
        print(chunk.content, end='', flush=True)
    print()