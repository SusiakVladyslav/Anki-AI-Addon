import aqt.utils
from aqt import mw
from aqt.browser import Browser

from anki.notes import Note

from ..utils.constants import CONFIG, ADDON_PACKAGE


def insert_profile_settings_in_config(profile_settings_dict: dict[str, dict[str, type]]):
    if CONFIG:
        profiles_dict = CONFIG.setdefault("Profiles", {})
        new_profile_name = next(iter(profile_settings_dict))

        if new_profile_name in profiles_dict:
            aqt.utils.showInfo("This profile already exist")
            return False
        else:
            profiles_dict.update(profile_settings_dict)
            mw.addonManager.writeConfig(ADDON_PACKAGE, CONFIG)
            return True
    else:
        aqt.utils.showInfo("Config not found")
        return False


def get_profile_settings_from_config(profile_name: str) -> dict[str, type]:
    profile_settings = CONFIG.get("Profiles")[profile_name]
    return profile_settings


def decide_price_format(price: float) -> str:
    three_digits_after_decimal_point_price = f"{price:.3f}"
    if three_digits_after_decimal_point_price.endswith("0"):
        return f"{price:.2f}"

    return three_digits_after_decimal_point_price


def create_table_check_item(checked: bool) -> aqt.qt.QTableWidgetItem:
    green = "#4CAF50"
    red = "#F44336"

    symbol = "✔" if checked else "✖"
    color = green if checked else red

    item = aqt.qt.QTableWidgetItem(symbol)
    item.setForeground(aqt.qt.QColor(color))
    item.setTextAlignment(aqt.Qt.AlignmentFlag.AlignCenter)
    return item


def get_selected_notes(browser: Browser) -> list[Note]:
    selected_notes_id = browser.selected_notes()
    selected_notes = [mw.col.get_note(note_id) for note_id in selected_notes_id]

    return selected_notes