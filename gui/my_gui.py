from aqt import mw, gui_hooks
from aqt.qt import *
from aqt.browser import Browser
from aqt.utils import showInfo, showWarning
from aqt.operations import QueryOp
from aqt.browser import Browser

from ..utils.constants import MODEL
from ..utils.func_utils import change_the_notes, calculate_spent_money


def on_browser_context_menu(browser):
    selected_card_ids = browser.selected_cards()
    showInfo(str(selected_card_ids))


def on_browser_context_menu_card_menu(browser, menu):
    action = menu.addAction("📥 Copy Note's fields to file")
    qconnect(action.triggered, lambda _=False: on_browser_context_menu(browser))


def gui_func(browser: Browser):
    msg = QMessageBox(browser)
    msg.setIcon(QMessageBox.Icon.Question)
    msg.setWindowTitle("Confirmation of used AI model")
    msg.setText(f"The used model is {MODEL}.\nDo you want to continue?")
    msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    result = msg.exec()

    if result == QMessageBox.StandardButton.Yes:
        QueryOp(
            parent=browser,
            op=lambda col: change_the_notes(browser),  # The function that runs in background
            success=on_success  # The function that will be called with the arguments of the op function when the op funtion is completed
        ).with_progress("AI is generating sentences...").run_in_background()


def on_success(result) -> None:
    browser, input_tokens, output_tokens, time_spent = result
    browser.table.reset()
    if browser.editor.note:
        browser.editor.loadNote()

    money_spent_on_input, money_spent_on_output, total_money_spent = calculate_spent_money(input_tokens, output_tokens, MODEL)

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
        f"Model: {MODEL}",
        parent=browser
    )


if __name__ == '__main__':
    pass

