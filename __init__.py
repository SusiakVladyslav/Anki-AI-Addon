from aqt import gui_hooks

from .gui.menus.browser_menu import setup_browser_menu
from .gui.menus.tools_menu import setup_tools_menu

setup_tools_menu()
gui_hooks.browser_menus_did_init.append(setup_browser_menu)

