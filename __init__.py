from aqt import gui_hooks

from .gui.browser_menu import setup_browser_menus
from .gui.main_menu import setup_tools_menu

setup_tools_menu()
gui_hooks.browser_menus_did_init.append(setup_browser_menus)

