import aqt.utils
from aqt import mw

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