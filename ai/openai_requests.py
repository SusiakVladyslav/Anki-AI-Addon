import time
import requests
from utils.constants import OPENAI_API_KEY, MODEL, PROMPT, AI_URL


def request_something(list_of_words="", prompt=PROMPT):
    start_time = time.time()

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
    end_time = time.time()
    time_spent = end_time - start_time

    result = response.json()

    output_text = result["output"][0]["content"][0]["text"]
    input_tokens = result["usage"]["input_tokens"]
    output_tokens = result["usage"]["output_tokens"]

    return output_text, time_spent, input_tokens, output_tokens


if __name__ == '__main__':
    print(request_something())
