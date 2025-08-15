from openai import OpenAI
from dotenv import load_dotenv
import os
import httpx
import argparse

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

# Define tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather of a location. User must supply a location first.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g., 合肥市",
                    }
                },
                "required": ["location"],
            },
        }
    },
]

def send_messages(messages):
    """Send messages to the model and return the response."""
    response = client.chat.completions.create(
        model=os.getenv("LLM_MODEL"),  # e.g., "gpt-3.5-turbo"
        messages=messages,
        tools=tools,
        tool_choice="auto"  # Let the model decide whether to use a tool
    )
    return response.choices[0].message

def main():
    """Main function to run the weather query example."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Get weather information for a city using LLM function calling")
    parser.add_argument("city", nargs="?", default="Hefei", help="City name to get weather for (default: Hefei)")
    args = parser.parse_args()
    
    # Initial user message
    messages = [{"role": "user", "content": f"How's the weather in {args.city}?"}]
    print(f"User> {messages[0]['content']}")

    # First call: Model decides to use a tool
    message = send_messages(messages)
    messages.append(message)

    # Check if a tool was called
    if message.tool_calls:
        tool_call = message.tool_calls[0]
        print(f"Model> {tool_call.function.name}({tool_call.function.arguments})")
        # refer to https://lbs.amap.com/api/webservice/guide/api-advanced/weatherinfo
        url = "https://restapi.amap.com/v3/weather/weatherInfo"
        params = {
            "city": get_city_code(tool_call.function.arguments),
            "key": os.getenv("LBS_API_KEY")
        }
        response = httpx.get(url, params=params, verify=False)
        """response example
        {
            "status": "1",
            "count": "1",
            "info": "OK",
            "infocode": "10000",
            "lives": [
                {
                    "province": "安徽",
                    "city": "合肥市",
                    "adcode": "340100",
                    "weather": "晴",
                    "temperature": "34",
                    "winddirection": "南",
                    "windpower": "≤3",
                    "humidity": "57",
                    "reporttime": "2025-08-14 16:03:34",
                    "temperature_float": "34.0",
                    "humidity_float": "57.0"
                }
            ]
        }
        """

        today_weather = response.json()["lives"][0]
        tool_response = today_weather["city"] + " is " + today_weather["weather"] + ", " + today_weather["temperature"] + "°C, at " + today_weather["reporttime"]

        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": tool_response
        })

        # Final call: Model generates natural language answer
        final_message = send_messages(messages)
        print(f"Model> {final_message.content}")
    else:
        # No tool called; model provided a direct answer
        print(f"Model> {message.content}")

if __name__ == "__main__":
    main()