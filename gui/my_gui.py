from aqt.qt import *
from aqt.utils import showInfo
from aqt.operations import QueryOp
from aqt.browser import Browser

from ..utils.constants import MODEL
from ..utils.func_utils import change_the_notes, calculate_spent_money
from gui.dialogs import successful_ingestion_of_generated_korean_sentences_info


def gui_func(browser: Browser) -> None:
    model_is_confirmed = confirmation_of_the_ai_model_message_box(browser)

    if model_is_confirmed:
        QueryOp(
            parent=browser,
            op=lambda col: change_the_notes(browser),  # The function that runs in background
            success=on_successful_ingestion  # The function that will be called with the arguments of the op function when the op funtion is completed
        ).with_progress("AI is generating sentences...").run_in_background()


def confirmation_of_the_ai_model_message_box(browser: Browser) -> bool:
    msg = QMessageBox(browser)
    msg.setIcon(QMessageBox.Icon.Question)
    msg.setWindowTitle("Confirmation of used AI model")
    msg.setText(f"The used model is {MODEL}.\nDo you want to continue?")
    msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    result = msg.exec()

    return result == QMessageBox.StandardButton.Yes


def on_successful_ingestion(result) -> None:
    browser, input_tokens, output_tokens, time_spent = result
    browser.table.reset()
    if browser.editor.note:
        browser.editor.loadNote()

    money_spent_on_input, money_spent_on_output, total_money_spent = calculate_spent_money(input_tokens, output_tokens, MODEL)

    successful_ingestion_of_generated_korean_sentences_info(
        time_spent=time_spent,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        money_spent_on_input=money_spent_on_input,
        money_spent_on_output=money_spent_on_output,
        total_money_spent=total_money_spent,
        model=MODEL,
        browser=browser
    )


if __name__ == '__main__':
    pass

