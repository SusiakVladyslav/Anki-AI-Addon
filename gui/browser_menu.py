from aqt.qt import QMenu, QAction, qconnect
from aqt.browser import Browser
import aqt

from .browser_gui import generate_sentences_for_selected_notes_action
from .create_profile_configuration import ProfileConfigurationDialog, DialogMode
from .apply_profile_window import ApplyProfileDialog
from .. utils.constants import CONFIG

def setup_browser_menus(browser: Browser) -> None:
    generation_profiles_menu = QMenu("AI Generation Profiles", browser)
    populate_ai_generation_profiles_menu(browser, generation_profiles_menu)

    my_menu = QMenu("My add-on", browser)
    populate_my_addon_menu(browser, my_menu)

    browser.form.menubar.addMenu(generation_profiles_menu)
    browser.form.menubar.addMenu(my_menu)

def populate_ai_generation_profiles_menu(browser: Browser, generation_profiles_menu: QMenu) -> None:
    generation_profiles_menu.clear()

    setup_profile_buttons(browser, generation_profiles_menu)
    generation_profiles_menu.addSeparator()

    create_profile_action = QAction("Create Profile", browser)
    qconnect(create_profile_action.triggered, lambda: open_configuration_dialog(browser, generation_profiles_menu))
    generation_profiles_menu.addAction(create_profile_action)

def open_configuration_dialog(browser: Browser, generation_profiles_menu) -> None:
    configuration_dialog = ProfileConfigurationDialog(mode=DialogMode.CREATE, parent=browser)
    configuration_dialog.accepted.connect(lambda: populate_ai_generation_profiles_menu(browser, generation_profiles_menu))
    configuration_dialog.open()

def setup_profile_buttons(browser: Browser, generation_profiles_menu: QMenu) -> None:
    profile_dicts = CONFIG.setdefault("Profiles", {})

    for profile_name, profile_settings in profile_dicts.items():
        profile_action = QAction(f"Profile {profile_name}", browser)

        # I need to save the profile_name in dialog_profile_name variable,
        # otherwise every button will trigger the function for the last profile in the dict
        qconnect(
            profile_action.triggered, lambda _, dialog_profile_name=profile_name:
            open_apply_profile_dialog(browser, dialog_profile_name, generation_profiles_menu)
        )

        generation_profiles_menu.addAction(profile_action)

def open_apply_profile_dialog(browser: Browser, profile_name: str, generation_profiles_menu) -> None:
    apply_profile_dialog = ApplyProfileDialog(browser, profile_name)
    apply_profile_dialog.finished.connect(lambda: populate_ai_generation_profiles_menu(browser, generation_profiles_menu))
    apply_profile_dialog.open()

def populate_my_addon_menu(browser: Browser, my_menu: QMenu) -> None:
    action = QAction("Generate sentences for selected Korean Notes", browser)
    qconnect(action.triggered, lambda: generate_sentences_for_selected_notes_action(browser))
    my_menu.addAction(action)
