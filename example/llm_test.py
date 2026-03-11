from openai import OpenAI
import sys


def test_llm(base_url, api_key, model):
    try:
        client = OpenAI(
            base_url=base_url,
            api_key=api_key,
        )

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": "say a jok"}
            ],
            max_tokens=10,
        )

        print("✅ API works!")
        print("Model:", model)
        print("Response:", response.choices[0].message.content)

    except Exception as e:
        print("❌ API failed")
        print("Error:", str(e))


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage:")
        print("python llm_test.py <base_url> <api_key> <model>")
        print("")
        print("Example:")
        print("python llm_test.py https://api.moonshot.cn/v1 sk-xxxx moonshot-v1-8k")
        sys.exit(1)

    base_url = sys.argv[1]
    api_key = sys.argv[2]
    model = sys.argv[3]

    test_llm(base_url, api_key, model)

