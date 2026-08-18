from aqt.qt import *
from aqt.utils import showInfo, showCritical
from aqt.operations import QueryOp
from aqt.browser import Browser

from ..utils.constants import MODEL
from ..utils.func_utils import generate_sentences_and_update_notes, calculate_spent_money, get_selected_notes
import gui.dialogs as dialogs
from ..utils.exceptions import NothingWasGenerated, LessThan3LinesGenerated, NumberOfLinesNotDivisibleBy3


def generate_sentences_for_selected_notes_action(browser: Browser) -> None:
    selected_notes = get_selected_notes(browser)

    if selected_notes is None:
        return

    model_is_confirmed = confirmation_of_the_ai_model_message_box(browser)

    if model_is_confirmed:
        op = QueryOp(
            parent=browser,
            op=lambda col: generate_sentences_and_update_notes(browser, selected_notes),  # The function that runs in background
            success=on_successful_generation_and_ingestion  # The function that will be called with the arguments of the op function when the op funtion is completed
        )

        op.with_progress("AI is generating sentences...").run_in_background()
        op.failure(lambda error: on_failed_generation_and_ingestion(browser, error))


def confirmation_of_the_ai_model_message_box(browser: Browser) -> bool:
    msg = QMessageBox(browser)
    msg.setIcon(QMessageBox.Icon.Question)
    msg.setWindowTitle("Confirmation of used AI model")
    msg.setText(f"The used model is {MODEL}.\nDo you want to continue?")
    msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    result = msg.exec()

    return result == QMessageBox.StandardButton.Yes


def on_successful_generation_and_ingestion(result) -> None:
    browser, input_tokens, output_tokens, time_spent = result

    browser.table.reset()
    if browser.editor.note:
        browser.editor.loadNote()

    money_spent_on_input, money_spent_on_output, total_money_spent = calculate_spent_money(input_tokens, output_tokens, MODEL)

    dialogs.successful_ingestion_of_generated_korean_sentences_info(
        time_spent=time_spent,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        money_spent_on_input=money_spent_on_input,
        money_spent_on_output=money_spent_on_output,
        total_money_spent=total_money_spent,
        model=MODEL,
        browser=browser
    )


def on_failed_generation_and_ingestion(browser: Browser, error: Exception) -> None:
    match error:
        case NothingWasGenerated():
            dialogs.nothing_was_generated_critical(browser)
        case LessThan3LinesGenerated():
            dialogs.less_than_3_lines_generated_critical(browser)
        case NumberOfLinesNotDivisibleBy3():
            dialogs.number_of_lines_is_not_divisible_by_3_critical(browser)
        case _:
            dialogs.unknown_generation_error_critical(browser, error)


if __name__ == '__main__':
    pass

