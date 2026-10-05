from aqt import gui_hooks
from aqt.qt import QMenu, QAction, qconnect

from .gui.browser_menu import setup_browser_menus

gui_hooks.browser_menus_did_init.append(setup_browser_menus)

