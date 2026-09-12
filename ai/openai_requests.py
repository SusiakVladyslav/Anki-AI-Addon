import requests
import time

from ..utils.constants import OPENAI_API_KEY, MODEL, AI_URL


def send_open_ai_request(input_data: str, prompt: str) -> tuple[str, int, int, int, float]:

    start_time = time.time()
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": MODEL,
        "input": prompt + input_data
        # "temperature": 2
    }

    response = requests.post(AI_URL, headers=headers, json=data, timeout=60)
    result = response.json()

    output_text, input_tokens, output_tokens, cache_input_tokens = extract_text_and_usage(result)

    return output_text, input_tokens, output_tokens, cache_input_tokens, time.time() - start_time


def extract_text_and_usage(result: dict[str: any]) -> tuple[str, int, int, int]:

    message_block = next(
        (item for item in result.get("output", []) if item.get("type") == "message"),
        None,
    )
    output_text = (
        message_block["content"][0]["text"]
        if message_block and message_block.get("content")
        else None
    )

    usage = result.get("usage", {})
    input_tokens = usage.get("input_tokens", 0)
    cache_input_tokens = usage.get("input_tokens_details", {}).get("cached_tokens", 0)
    output_tokens = usage.get("output_tokens", 0)


    return output_text, input_tokens, output_tokens, cache_input_tokens


if __name__ == '__main__':
    pass
