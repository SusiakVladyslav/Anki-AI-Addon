import time

from anki.notes import Note

from ai.openai_requests import request_something


def make_ai_request(selected_notes: list[Note], prompt: str) -> tuple[str, int, int, float]:
    all_notes_fields_str = get_notes_fields_as_string(selected_notes)

    start_time = time.time()
    output_text, input_tokens, output_tokens, cache_input_tokens = request_something(all_notes_fields_str, prompt=prompt)
    time_spent = time.time() - start_time

    return output_text, input_tokens, output_tokens, time_spent


def get_notes_fields_as_string(selected_notes: list[Note]) -> str:
    all_notes_fields_str = ""
    for note in selected_notes:
        fields_data: list[tuple[str, str]] = note.items()
        for field_name, field_value in fields_data:
            if field_name == "Audio" or field_name == "Number" or field_name == "Hanja":
                continue
            all_notes_fields_str += f"{field_name}|{field_value}\n"

    return all_notes_fields_str
