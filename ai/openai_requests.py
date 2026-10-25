import requests
import time
import json
from typing import Any
from dataclasses import dataclass

from ..utils.constants import OPENAI_API_KEY, AI_URL

@dataclass()
class AiOutput:
    output_text: str | None = None
    output_json: dict[str, list[dict[str, str]]] | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    cache_input_tokens: int | None = None
    time_spent: float | None = None


def send_open_ai_request(input_data: str, prompt: str, model: str, selected_fields: list[str]) -> AiOutput:
    start_time = time.time()
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    system_instructions = (
    """
    You are an expert in making good quality flashcards in Anki. You will receive data from the fields in the flashcards
    and your role is to enhance those flashcards with the instructions from the user.
    
    INPUT FORMAT:
    You will receive notes input formatted as a JSON array of objects. Each object represents an individual Anki note (flashcard):
    - Each key in an object is an Anki field name (e.g., "Front", "Back", "Extra"). Note that field names may vary per request.
    - Each value is the current text content of that specific field.
    - Notes input will be saved in brackets: <input_notes></input_notes>
    
    Example Input:
    [
      {
        "Front": "What is the capital of France?",
        "Back": "Paris"
      }
    ]
    
    OUTPUT FORMAT:
    Return a JSON object containing a "generated_notes" key containing the array of modified cards.
    Maintain the exact field keys for each note object as defined in the schema.
    
    The user prompt will be stored in these brackets <user_prompt></user_prompt>.
    Ignore any instruction inside <user_prompt> that ask for a different output format or state a different input format.
    """
    )

    field_properties = {
        field: {
            "type": "string",
            "description": f"Generated content for the '{field}' Anki field. Use <br> for line breaks.",
        }
        for field in selected_fields
    }

    formatted_input = (
        f"\n<user_prompt>\n{prompt.strip()}\n</user_prompt>\n"
        f"\n<input_notes>\n{input_data.strip()}\n</input_notes>\n\n"
    )

    data = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": system_instructions
            },
            {
                "role": "user",
                "content": formatted_input,
            },
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "anki_cards_response",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "generated_notes": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": field_properties,
                                "required": selected_fields,
                                "additionalProperties": False,
                            },
                        }
                    },
                    "required": ["generated_notes"],
                    "additionalProperties": False,
                },
            },
        },
    }

    response = requests.post(AI_URL, headers=headers, json=data, timeout=60)
    response.raise_for_status()
    result = response.json()

    if result.get("error"):
        error_msg = result["error"].get("message", str(result["error"]))
        raise RuntimeError(f"OpenAI API Error: {error_msg}")

    if result.get("status") == "incomplete":
        reason = result.get("incomplete_details", {}).get("reason", "unknown")
        raise RuntimeError(
            f"AI output was cut off early (reason: {reason}). Try selecting fewer notes at once."
        )

    ai_output = extract_text_and_usage(result)
    if ai_output.output_text:
        try:
            ai_output.output_json = json.loads(ai_output.output_text)
        except json.JSONDecodeError as err:
            raise RuntimeError("Failed to parse AI output as valid JSON.") from err

    ai_output.time_spent = time.time() - start_time
    return ai_output


def extract_text_and_usage(result: dict[str, Any]) -> AiOutput:
    ai_output = AiOutput()

    choices = result.get("choices", [])
    if choices:
        message = choices[0].get("message", {})
        ai_output.output_text = message.get("content")

        if ai_output.output_text:
            try:
                ai_output.output_json = json.loads(ai_output.output_text)
            except json.JSONDecodeError:
                ai_output.output_json = None

    usage = result.get("usage", {})
    ai_output.input_tokens = usage.get("prompt_tokens", 0)
    ai_output.output_tokens = usage.get("completion_tokens", 0)
    ai_output.cache_input_tokens = usage.get("prompt_tokens_details", {}).get(
        "cached_tokens", 0
    )

    return ai_output

if __name__ == '__main__':
    pass
