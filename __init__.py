from aqt import gui_hooks
from aqt.qt import QMenu, QAction, qconnect

from .ai.OpenAI_Anki import write_ai_output_to_file, generate_audios
from .utils.func_utils import write_notes_to_file, write_file_to_notes, change_the_notes
from .gui.my_gui import on_browser_context_menu, on_browser_context_menu_card_menu, gui_func


def setup_browser_menu(browser):
    my_menu = QMenu("My add-on", browser)
    browser.form.menubar.addMenu(my_menu)

    # 2. Add actions
    Transfer_Notes_to_file = QAction("📥 Copy Note's fields to file", browser)
    # Pass 'browser' to your function if it needs access to selected cards/notes
    qconnect(Transfer_Notes_to_file.triggered, write_notes_to_file)
    my_menu.addAction(Transfer_Notes_to_file)

    AI_to_file = QAction("🤖 Ask AI to generate sentences", browser)
    qconnect(AI_to_file.triggered, write_ai_output_to_file)
    my_menu.addAction(AI_to_file)

    TTS_audios = QAction("🔊 Ask AI to generate audios", browser)
    qconnect(TTS_audios.triggered, generate_audios)
    my_menu.addAction(TTS_audios)

    Transfer_file_to_Notes = QAction("📤 Transfer sentences and audio to Notes", browser)
    qconnect(Transfer_file_to_Notes.triggered, write_file_to_notes)
    my_menu.addAction(Transfer_file_to_Notes)

    action = QAction("Copy Notes", browser)
    # Use lambda _=False or ignore signal arguments explicitly:
    qconnect(action.triggered, lambda _=False: on_browser_context_menu(browser))
    my_menu.addAction(action)

    action = QAction("Test func", browser)
    # Use lambda _=False or ignore signal arguments explicitly:
    qconnect(action.triggered, lambda _=False: gui_func(browser))
    my_menu.addAction(action)


# 3. Register hook to run when the Browser window initializes
gui_hooks.browser_menus_did_init.append(setup_browser_menu)
# gui_hooks.browser_will_show_context_menu.append(on_browser_context_menu_card_menu)  # it will happen inside card menu, when you click on a card with a right click

