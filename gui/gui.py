from aqt import mw, gui_hooks
from aqt.qt import *
from aqt.browser import Browser
from aqt.utils import showInfo, showWarning


def on_browser_context_menu(browser):
    selected_card_ids = browser.selected_cards()
    showInfo(str(selected_card_ids))


def on_browser_context_menu_card_menu(browser, menu):
    action = menu.addAction("📥 Copy Note's fields to file")
    qconnect(action.triggered, lambda _=False: on_browser_context_menu(browser))


if __name__ == '__main__':
    pass

