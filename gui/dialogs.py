from aqt.browser import Browser
from aqt.utils import showInfo, showWarning, showCritical


def more_than_one_note_type_selected_warning() -> None:
    showWarning("More than 1 note type selected")


def no_cards_were_selected_warning() -> None:
    showWarning("No cards were selected")


def nothing_was_generated_critical() -> None:
    showCritical("AI didn't generate anything.")


def less_than_3_lines_generated_critical() -> None:
    showCritical("Unexpected amount of lines. The amount of generated lines is less than 3")


def number_of_lines_is_not_divisible_by_3_critical() -> None:
    showCritical("Unexpected amount of lines. The amount of generated lines is not divisible by 3")


def successful_ingestion_of_generated_korean_sentences_info(
        time_spent: float,
        input_tokens: int,
        output_tokens: int,
        money_spent_on_input: float,
        money_spent_on_output: float,
        total_money_spent: float,
        model: str,
        browser: Browser) -> None:
    showInfo(
        f"AI response written successfully!\n"
        f"Time spent: {time_spent:.3f} seconds\n"
        f"\n"
        f"Input tokens used: {input_tokens}\n"
        f"Output tokens used: {output_tokens}\n"
        f"\n"
        f"Money spent on input {money_spent_on_input:.5f}$\n"
        f"Money spent on output {money_spent_on_output:.5f}$\n"
        f"Total money spent {total_money_spent:.5f}$\n"
        f"\n"
        f"Model: {model}",
        parent=browser
    )
