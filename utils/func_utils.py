import html
import re
import itertools

from aqt import mw
from aqt.browser import Browser

from anki.notes import Note

from utils.constants import PROMPT, EMPTY_LINE, MODELS_INPUT_PRICES, MODELS_OUTPUT_PRICES
import gui.dialogs as dialogs
from ..ai import openai_requests as openai


def strip_html(text):
    """Remove HTML tags and decode HTML entities"""
    if not text:
        return ""

    # First, decode HTML entities like &amp; &lt; &gt;
    text = html.unescape(text)

    # Remove HTML tags using regex
    clean_text = re.sub(r'<[^>]+>', '', text)

    # Clean up extra whitespace
    clean_text = ' '.join(clean_text.split())

    return clean_text


def calculate_spent_money(input_tokens: int, output_tokens: int, model: str) -> tuple[float, float, float]:
    price_per_1_million_input_tokens = MODELS_INPUT_PRICES[model]
    price_per_1_million_output_tokens_price = MODELS_OUTPUT_PRICES[model]
    money_spent_on_input = (input_tokens / 1000000) * price_per_1_million_input_tokens
    money_spent_on_output = (output_tokens / 1000000) * price_per_1_million_output_tokens_price
    total_money_spent = money_spent_on_input + money_spent_on_output

    return money_spent_on_input, money_spent_on_output, total_money_spent


def get_selected_notes(browser: Browser) -> list[Note] | None:
    selected_note_ids = browser.selected_notes()
    selected_notes = [mw.col.get_note(note_id) for note_id in selected_note_ids]

    if len(selected_notes) == 0:
        dialogs.no_cards_were_selected_warning()
        return

    if more_than_one_note_type_selected(selected_notes):
        dialogs.more_than_one_note_type_selected_warning()
        return

    return selected_notes


def more_than_one_note_type_selected(selected_notes: list[Note]) -> bool:
    set_of_note_types = set(note.note_type()["name"] for note in selected_notes)

    if len(set_of_note_types) > 1:
        return True
    else:
        return False


def generate_sentences_and_update_notes(browser: Browser, selected_notes: list[Note]) -> tuple[Browser, int, int, float] | None:
    notes_fields_str = get_notes_fields_as_string(selected_notes)

    (output_text,
     input_tokens,
     output_tokens,
     cached_input_tokens,
     time_spent) = openai.send_open_ai_request(input_data=notes_fields_str, prompt=PROMPT)

    ingest_output_text(output_text, selected_notes)

    return browser, input_tokens, output_tokens, time_spent


def get_notes_fields_as_string(selected_notes: list[Note]) -> str:
    all_notes_fields_str = ""
    for note in selected_notes:
        fields_data: list[tuple[str, str]] = note.items()
        for field_name, field_value in fields_data:
            if field_name == "Audio" or field_name == "Number" or field_name == "Hanja":
                continue
            all_notes_fields_str += f"{field_name}|{field_value}\n"

    return all_notes_fields_str


def ingest_output_text(output_text: str, selected_notes: list[Note]) -> None:
    lines = [line.strip() for line in output_text.splitlines() if line.strip()]

    for n, (kor, vocab, eng) in enumerate(itertools.batched(lines, 3)):
        note = selected_notes[n]
        for field_name in note.keys():
            if field_name == "Korean":
                note[field_name] = kor
            if field_name == "English":
                note[field_name] = vocab + EMPTY_LINE + eng

        note.col.update_note(note)


if __name__ == '__main__':
    pass
