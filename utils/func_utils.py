import html
import re
import itertools

from aqt import mw
from aqt.browser import Browser

from anki.notes import Note

from utils.constants import PROMPT, EMPTY_LINE, MODELS_INPUT_PRICES, MODELS_OUTPUT_PRICES
import gui.dialogs as dialogs
from ..ai import OpenAI_Anki as open_ai


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


def change_the_notes(browser: Browser) -> tuple[Browser, int, int, float] | None:
    selected_notes = get_selected_notes(browser)

    if selected_notes is None:
        return

    type_of_notes = selected_notes[0].note_type()["name"]

    output_text, input_tokens, output_tokens, time_spent = open_ai.make_ai_request(selected_notes, prompt=PROMPT)

    ingest_output_text(output_text, selected_notes)

    return browser, input_tokens, output_tokens, time_spent


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


def ingest_output_text(output_text: str, selected_notes: list[Note]) -> None:
    lines = [line.strip() for line in output_text.splitlines() if line.strip()]

    if lines is []:
        dialogs.nothing_was_generated_critical()
        return

    if len(lines) < 3:
        dialogs.less_than_3_lines_generated_critical()
        return

    if len(lines) % 3 != 0:
        dialogs.number_of_lines_is_not_divisible_by_3_critical()
        return

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
