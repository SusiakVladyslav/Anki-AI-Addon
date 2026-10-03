from aqt import gui_hooks
from aqt.qt import QMenu, QAction, qconnect

from .gui.browser_gui import generate_sentences_for_selected_notes_action
from .gui.create_profile_configuration import *


def setup_browser_menu(browser) -> None:
    my_menu = QMenu("My add-on", browser)
    browser.form.menubar.addMenu(my_menu)

    action = QAction("Generate sentences for selected Korean Notes", browser)
    qconnect(action.triggered, lambda _=False: generate_sentences_for_selected_notes_action(browser))
    my_menu.addAction(action)

    window_action = QAction("Create profile window", browser)
    qconnect(window_action.triggered, lambda _=False: open_configuration_dialog(browser))
    my_menu.addAction(window_action)


gui_hooks.browser_menus_did_init.append(setup_browser_menu)

