import requests
from utils.constants import OPENAI_API_KEY, MODEL, PROMPT, AI_URL


def request_something(list_of_words: str = "", prompt: str = PROMPT) -> tuple[str, int, int]:
    result = fetch_response(list_of_words, prompt)

    output_text = result["output"][0]["content"][0]["text"]
    input_tokens = result["usage"]["input_tokens"]
    cache_input_tokens = result["usage"]["input_tokens_details"]["cached_tokens"]
    output_tokens = result["usage"]["output_tokens"]

    return output_text, input_tokens, output_tokens, cache_input_tokens


def fetch_response(list_of_words: str, prompt: str) -> dict:
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": MODEL,
        "input": prompt + list_of_words
        # "temperature": 2
    }

    response = requests.post(AI_URL, headers=headers, json=data)
    result = response.json()

    return result


if __name__ == '__main__':
    print(request_something())
