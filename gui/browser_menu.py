from aqt.qt import QMenu, QAction, qconnect
from aqt.browser import Browser
import aqt

from .browser_gui import generate_sentences_for_selected_notes_action
from .create_profile_configuration import ProfileConfigurationDialog, DialogMode
from .apply_profile_window import ApplyProfileDialog
from .. utils.constants import CONFIG, MAX_NOTES_TO_APPLY
from . import style, gui_utils
from . import dialogs


def setup_browser_menus(browser: Browser) -> None:
    generation_profiles_menu = QMenu("AI Generation Profiles", browser)
    populate_ai_generation_profiles_menu(generation_profiles_menu, browser)

    my_menu = QMenu("My add-on", browser)
    populate_my_addon_menu(browser, my_menu)

    browser.form.menubar.addMenu(generation_profiles_menu)
    browser.form.menubar.addMenu(my_menu)


def populate_ai_generation_profiles_menu(generation_profiles_menu: QMenu, browser: Browser) -> None:
    generation_profiles_menu.clear()
    profile_dicts = CONFIG.setdefault("Profiles", {})
    profile_names = list(profile_dicts.keys())

    if len(profile_names) > style.MAX_VISIBLE_PROFILES:
        setup_scrollable_profile_buttons(generation_profiles_menu, profile_names, browser)
    else:
        setup_standard_profile_buttons(generation_profiles_menu, profile_names, browser)

    generation_profiles_menu.addSeparator()

    create_profile_action = QAction("Create Profile...", browser)
    qconnect(
        create_profile_action.triggered,
        lambda: open_configuration_dialog(browser, generation_profiles_menu)
    )
    generation_profiles_menu.addAction(create_profile_action)

def setup_scrollable_profile_buttons(generation_profiles_menu: QMenu, profile_names: list[str], browser: Browser) -> None:
    scroll_area = aqt.qt.QScrollArea(generation_profiles_menu)
    scroll_area.setWidgetResizable(True)
    scroll_area.setHorizontalScrollBarPolicy(aqt.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    scroll_area.setVerticalScrollBarPolicy(aqt.Qt.ScrollBarPolicy.ScrollBarAsNeeded)

    scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")  # Removes border in the menu

    container_widget = aqt.qt.QWidget()
    container_widget.setStyleSheet("background: transparent;")  # Makes scrollable area have the same color as the menu

    layout = aqt.qt.QVBoxLayout(container_widget)
    layout.setContentsMargins(0,0,0,0)
    layout.setSpacing(0)

    for profile_name in profile_names:
        btn = aqt.qt.QPushButton(profile_name)
        btn.setToolTip(profile_name)
        btn.setFixedHeight(style.MENU_BUTTON_HEIGHT)
        btn.setCursor(aqt.Qt.CursorShape.PointingHandCursor)  # It changes the cursor to pointing hand on hover

        btn.setStyleSheet(f"""
                    QPushButton {{
                        text-align: left;
                        padding: {style.MENU_BUTTON_LR_PADDING}px {style.MENU_BUTTON_TB_PADDING}px;
                        border: none;
                        background: transparent;
                    }}
                    QPushButton:hover {{
                        background-color: {style.MENU_BUTTON_HOVER_BG_COLOR};
                    }}
                """)

        btn.clicked.connect(
            lambda _, p_name=profile_name: open_apply_profile_dialog(browser, p_name, generation_profiles_menu)
        )
        layout.addWidget(btn)

    container_widget.setLayout(layout)
    scroll_area.setWidget(container_widget)

    min_menu_width = style.MIN_SCROLLABLE_MENU_WIDTH
    longest_profile_width = gui_utils.calculate_longest_profile_width(generation_profiles_menu, profile_names)

    width_padding = 40
    height_padding = 8
    calculated_width = max(min_menu_width, longest_profile_width + width_padding)
    calculated_height = (style.MAX_VISIBLE_PROFILES * style.MENU_BUTTON_HEIGHT) + height_padding

    scroll_area.setFixedHeight(calculated_height)
    scroll_area.setFixedWidth(calculated_width)

    widget_action = aqt.qt.QWidgetAction(generation_profiles_menu)
    widget_action.setDefaultWidget(scroll_area)
    generation_profiles_menu.addAction(widget_action)

def setup_standard_profile_buttons(generation_profiles_menu: QMenu, profile_names: list[str], browser: Browser) -> None:
    for profile_name in profile_names:
        profile_action = QAction(f"Profile {profile_name}", browser)

        # I need to save the profile_name in dialog_profile_name variable,
        # otherwise every button will trigger the function for the last profile in the dict
        qconnect(
            profile_action.triggered, lambda _, dialog_profile_name=profile_name:
            open_apply_profile_dialog(browser, dialog_profile_name, generation_profiles_menu)
        )

        generation_profiles_menu.addAction(profile_action)

def open_apply_profile_dialog(browser: Browser, profile_name: str, generation_profiles_menu) -> None:
    selected_notes = gui_utils.get_selected_notes(browser)

    if len(selected_notes) < MAX_NOTES_TO_APPLY:
        apply_profile_dialog = ApplyProfileDialog(browser, profile_name, selected_notes)
        apply_profile_dialog.finished.connect(lambda: populate_ai_generation_profiles_menu(generation_profiles_menu, browser))
        apply_profile_dialog.open()
    else:
        dialogs.too_many_notes_were_selected_warning(parent=browser)

def open_configuration_dialog(browser: Browser, generation_profiles_menu: QMenu) -> None:
    configuration_dialog = ProfileConfigurationDialog(mode=DialogMode.Create, parent=browser)
    configuration_dialog.accepted.connect(lambda: populate_ai_generation_profiles_menu(generation_profiles_menu, browser))
    configuration_dialog.open()

def populate_my_addon_menu(browser: Browser, my_menu: QMenu) -> None:
    action = QAction("Generate sentences for selected Korean Notes", browser)
    qconnect(action.triggered, lambda: generate_sentences_for_selected_notes_action(browser))
    my_menu.addAction(action)
