from typing import List
import tiktoken
from langchain_core.messages import SystemMessage, trim_messages, BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.messages import trim_messages


def str_token_counter(text: str) -> int:
    enc = tiktoken.get_encoding("o200k_base")
    return len(enc.encode(text))

def tiktoken_counter(messages: List[BaseMessage]) -> int:
    num_tokens = 3
    tokens_per_message = 3
    tokens_per_name = 1
    for msg in messages:
        if isinstance(msg, HumanMessage):
            role = "user"
        elif isinstance(msg, AIMessage):
            role = "assistant"
        elif isinstance(msg, ToolMessage):
            role = "tool"
        elif isinstance(msg, SystemMessage):
            role = "system"
        else:
            raise ValueError(f"Unsupported messages type {msg.__class__}")
        num_tokens += (
                tokens_per_message
                + str_token_counter(role)
                + str_token_counter(msg.content)
        )
        if msg.name:
            num_tokens += tokens_per_name + str_token_counter(msg.name)
    return num_tokens

def create_message_trimmer(max_tokens: int = 4096, strategy: str = "last", token_counter: callable = tiktoken_counter, include_system: bool = True):
    trimmer = trim_messages(
        max_tokens=max_tokens,
        strategy=strategy,
        token_counter=token_counter,
        include_system=include_system,
    )
    return trimmer

