
from openai import OpenAI

# user should set `base_url="https://api.deepseek.com/beta"` to use this feature.
client = OpenAI(
  api_key="<your API key>",
  base_url="https://api.deepseek.com/beta",
)
response = client.completions.create(
  model="deepseek-coder",
  prompt="def fib(a):",
  suffix="    return fib(a-1) + fib(a-2)",
  max_tokens=128)
print(response.choices[0].text)