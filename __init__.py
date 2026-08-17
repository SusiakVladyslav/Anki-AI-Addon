from aqt import gui_hooks
from aqt.qt import QMenu, QAction, qconnect

from .gui.my_gui import gui_func


def setup_browser_menu(browser) -> None:
    my_menu = QMenu("My add-on", browser)
    browser.form.menubar.addMenu(my_menu)

    action = QAction("Generate sentences for selected Korean Notes", browser)
    qconnect(action.triggered, lambda _=False: gui_func(browser))
    my_menu.addAction(action)


# 3. Register hook to run when the Browser window initializes
gui_hooks.browser_menus_did_init.append(setup_browser_menu)
# gui_hooks.browser_will_show_context_menu.append(on_browser_context_menu_card_menu)  # it will happen inside card menu, when you click on a card with a right click

