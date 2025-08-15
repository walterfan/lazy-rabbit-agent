from openai import OpenAI
from dotenv import load_dotenv
import os
import httpx
import argparse
import json
import re

load_dotenv()

CITY_CODES = {
    "合肥市": "340100",
    "合肥": "340100",
    "HEFEI": "340100",
    "芜湖市": "340200",
    "芜湖": "340200",
    "WUHU": "340200"
}

# Initialize OpenAI client
http_client = httpx.Client(verify=False)  # Avoid in production!
client = OpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL"),  # e.g., "https://api.openai.com/v1"
    http_client=http_client
)

def get_city_code(city_name):
    city_name = city_name.strip().upper()
    return CITY_CODES.get(city_name, "340100")

def get_weather(city_name):
    """Get weather information for a city from the weather API."""
    # refer to https://lbs.amap.com/api/webservice/guide/api-advanced/weatherinfo
    url = "https://restapi.amap.com/v3/weather/weatherInfo"
    params = {
        "city": get_city_code(city_name),
        "key": os.getenv("LBS_API_KEY")
    }
    response = httpx.get(url, params=params, verify=False)
    
    today_weather = response.json()["lives"][0]
    return today_weather["city"] + " is " + today_weather["weather"] + ", " + today_weather["temperature"] + "°C, at " + today_weather["reporttime"]

def search_wiki(query):
    """Search Wikipedia and return a fake result for demonstration purposes."""
    # This is a fake implementation for demonstration
    fake_results = {
        "python": "Python is a high-level, interpreted programming language known for its simplicity and readability. It was created by Guido van Rossum and first released in 1991.",
        "artificial intelligence": "Artificial Intelligence (AI) is a branch of computer science that aims to create systems capable of performing tasks that typically require human intelligence.",
        "machine learning": "Machine Learning is a subset of AI that enables computers to learn and improve from experience without being explicitly programmed.",
        "weather": "Weather refers to the state of the atmosphere at a particular place and time, including temperature, humidity, precipitation, and wind conditions.",
        "default": f"'{query}' is a topic that could be found on Wikipedia. This is a simulated response for demonstration purposes."
    }
    
    # Return a relevant fake result if available, otherwise return the default
    query_lower = query.lower()
    for key, result in fake_results.items():
        if key in query_lower:
            return result
    
    return fake_results["default"]

tools_list = """
1. get_weather(city: str) - Returns the current weather for a given city.
2. search_wik(query: str) - Returns a summary from Wikipedia for the given query.
"""

# System prompt with embedded tools list
system_prompt = f"""
You are a helpful AI assistant.
You have the following tools available to you:
Available Tools: {tools_list}

If you decide to use a tool, respond ONLY with a valid JSON object:
{{ "tools":
  [
    {{ "name": "<tool_name>", "arguments": {{ ... }} }}
  ]
}}

If you do not use a tool, respond normally in plain text.
"""

user_prompt = "What's the weather like in Hefei right now?"

def send_messages(messages):
    """Send messages to the model and return the response."""
    response = client.chat.completions.create(
        model=os.getenv("LLM_MODEL"),  # e.g., "gpt-3.5-turbo"
        messages=messages,
        tool_choice="auto"  # Let the model decide whether to use a tool
    )
    return response.choices[0].message

def parse_and_execute_tools(message_content):
    """Parse JSON response from model and execute tool calls."""
    try:
        # Try to extract JSON from the message content
        # Look for JSON content that might be embedded in the text
        json_match = re.search(r'\{.*\}', message_content, re.DOTALL)
        if not json_match:
            return None, "No JSON found in response"
        
        json_str = json_match.group(0)
        data = json.loads(json_str)
        
        # Check if it's a tools call
        if "tools" in data and isinstance(data["tools"], list):
            results = []
            for tool_call in data["tools"]:
                if "name" in tool_call and "arguments" in tool_call:
                    tool_name = tool_call["name"]
                    arguments = tool_call["arguments"]
                    
                    # Execute the appropriate function based on tool name
                    if tool_name == "get_weather":
                        if "city" in arguments:
                            result = get_weather(arguments["city"])
                            results.append(f"get_weather({arguments['city']}) -> {result}")
                        else:
                            results.append("get_weather called but no city provided")
                    
                    elif tool_name == "search_wiki":
                        if "query" in arguments:
                            result = search_wiki(arguments["query"])
                            results.append(f"search_wiki({arguments['query']}) -> {result}")
                        else:
                            results.append("search_wiki called but no query provided")
                    
                    else:
                        results.append(f"Unknown tool: {tool_name}")
            
            return True, "\n".join(results)
        
        return None, "No valid tools structure found in JSON"
    
    except json.JSONDecodeError as e:
        return None, f"Failed to parse JSON: {e}"
    except Exception as e:
        return None, f"Error executing tools: {e}"

def main():
    """Main function to run the weather query example."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Get weather information for a city using LLM function calling")
    parser.add_argument("city", nargs="?", default="Hefei", help="City name to get weather for (default: Hefei)")
    args = parser.parse_args()
    
    # Initial user message
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    print(f"User> {messages[0]['content']}")

    # First call: Model decides to use a tool
    message = send_messages(messages)
    print(f"Model> message: {message}")
    messages.append(message)

    # Check if a tool was called
    if message.tool_calls:
        tool_call = message.tool_calls[0]
        print(f"Model> {tool_call.function.name}({tool_call.function.arguments})")
        
        # Get weather information using the extracted function
        tool_response = get_weather(tool_call.function.arguments)

        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": tool_response
        })

        # Final call: Model generates natural language answer
        final_message = send_messages(messages)
        print(f"Model> {final_message.content}")
    else:
        # Check if the message contains JSON tool calls
        success, result = parse_and_execute_tools(message.content)
        if success:
            print(f"Tools executed successfully:\n{result}")
            
            # Add tool response to messages
            messages.append({
                "role": "assistant",
                "content": f"Tools executed: {result}"
            })
            
            # Final call: Model generates natural language answer
            final_message = send_messages(messages)
            print(f"Model> {final_message.content}")
        else:
            # No tool called; model provided a direct answer
            print(f"Model> {message.content}")

if __name__ == "__main__":
    main()