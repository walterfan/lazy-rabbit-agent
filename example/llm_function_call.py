import simple_llm_agent

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather of an location, the user shoud supply a location first",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    }
                },
                "required": ["location"]
            },
        }
    },
]
"""
1) 用户：询问现在的天气
2) 模型：返回 function get_weather({location: 'Hangzhou'})
3) 用户：调用 function get_weather({location: 'Hangzhou'})，并传给模型。
4) 模型：返回自然语言，"The current temperature in Hangzhou is 24°C."
"""
llm_agent = simple_llm_agent.LlmAgent()
messages = [{"role": "user", "content": "How's the weather in Hangzhou?"}]
print(f"User>\t {messages[0]['content']}")

message = llm_agent.send_messages(messages, tools)
print(f"Model>\t {message}")

tool = message.tool_calls[0]
messages.append(message)

messages.append({"role": "tool", "tool_call_id": tool.id, "content": "24℃"})
print(f"User>\t {messages}")

message = llm_agent.send_messages(messages, tools)
print(f"Model>\t {message.content}")