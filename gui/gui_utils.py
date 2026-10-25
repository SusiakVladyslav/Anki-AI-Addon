import aqt.utils
from aqt import mw
from aqt.browser import Browser

from anki.notes import Note

from typing import Any
import html
import re

from ..utils.constants import CONFIG, ADDON_PACKAGE


def insert_profile_settings_in_config(profile_settings_dict: dict[str, dict[str, Any]]):
    if CONFIG:
        profiles_dict = CONFIG.setdefault("Profiles", {})
        profile_name = next(iter(profile_settings_dict))

        if profile_name in profiles_dict:
            aqt.utils.showInfo("This profile already exist")
            return False
        else:
            profiles_dict.update(profile_settings_dict)
            mw.addonManager.writeConfig(ADDON_PACKAGE, CONFIG)
            return True
    else:
        aqt.utils.showInfo("Config not found")
        return False

def update_profile_settings(original_profile_name, edited_profile_settings_dict: dict[str, dict[str, Any]]):
    if CONFIG:
        profiles_dict = CONFIG.setdefault("Profiles", {})
        edited_profile_name = next(iter(edited_profile_settings_dict))

        if original_profile_name == edited_profile_name:
            profiles_dict.update(edited_profile_settings_dict)

        else:
            if edited_profile_name in profiles_dict:
                aqt.utils.showInfo(f"Profile with name {edited_profile_name} already exist")
                return False

            new_profiles_dict = sort_profiles_dict(original_profile_name, edited_profile_settings_dict, profiles_dict)
            profiles_dict.clear()
            profiles_dict.update(new_profiles_dict)

        mw.addonManager.writeConfig(ADDON_PACKAGE, CONFIG)

        return True

    else:
        aqt.utils.showInfo("Config not found")
        return False


def update_profile_settings_name(profile_settings_dict, profile_name_was_edited: bool, original_profile_name: str | None=None):
    if CONFIG:
        profiles_dict = CONFIG.setdefault("Profiles", {})
    else:
        aqt.utils.showInfo("Config not found")
        return False

    profile_name = next(iter(profile_settings_dict))

    if profile_name_was_edited:
        if profile_name in profiles_dict:
            aqt.utils.showInfo(f"Profile with name {profile_name} already exist")
            return False

        if not original_profile_name:
            return False

        new_profiles_dict = sort_profiles_dict(original_profile_name, profile_settings_dict, profiles_dict)
        profiles_dict.clear()
        profiles_dict.update(new_profiles_dict)
    else:
        profiles_dict.update(profile_settings_dict)

    mw.addonManager.writeConfig(ADDON_PACKAGE, CONFIG)
    return True



def sort_profiles_dict(original_profile_name: str, edited_profile_settings_dict: dict[str, dict[str, Any]], profiles_dict):
    new_profiles_dict = dict()
    edited_profile_name = next(iter(edited_profile_settings_dict))

    for profile_name, profile_settings in profiles_dict.items():
        if profile_name == original_profile_name:
            new_profiles_dict.update(edited_profile_settings_dict)
        else:
            new_profiles_dict[profile_name] = profile_settings

    return new_profiles_dict


def delete_profile_from_config(profile_name: str):
    profiles = CONFIG.setdefault("Profiles", {})
    profiles.pop(profile_name)

    mw.addonManager.writeConfig(ADDON_PACKAGE, CONFIG)

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

# 1. Match <style> and <script> blocks with their inner content
_STYLE_SCRIPT_RE = re.compile(
    r"<(style|script)\b[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL
)

# 2. Match both opening AND closing block-level tags (including <summary> and <details>)
_BLOCK_TAG_RE = re.compile(
    r"</?(?:br|div|p|li|tr|td|th|summary|details|h[1-6]|blockquote|section|article|header|footer|hr|ul|ol|table|dl|dt|dd)\b[^>]*>",
    re.IGNORECASE,
)

# 3. Match any remaining inline tags (<span>, <b>, <i>, <a>, <ruby>, etc.)
_INLINE_TAG_RE = re.compile(r"<[^>]+>")


def strip_html(text: str) -> str:
    if not text:
        return ""

    # 1. Remove <style> and <script> blocks completely
    cleaned = _STYLE_SCRIPT_RE.sub("", text)

    # 2. Replace all block-level tags (opening and closing) with a newline
    cleaned = _BLOCK_TAG_RE.sub("\n", cleaned)

    # 3. Remove inline tags WITHOUT adding spaces (keeps "대학생<span>치고서</span>" attached)
    cleaned = _INLINE_TAG_RE.sub("", cleaned)

    # 4. Decode HTML entities (&nbsp;, &lt;, &gt;, &amp;) AFTER tags are removed
    cleaned = html.unescape(cleaned)

    # 5. Normalize non-breaking spaces (\xa0) and strip empty lines
    cleaned = cleaned.replace("\xa0", " ")
    lines = [line.strip() for line in cleaned.splitlines() if line.strip()]

    return "\n".join(lines)

def get_colored_icon(svg_path: str, color: aqt.qt.QColor) -> aqt.qt.QIcon:
    pixmap = aqt.qt.QPixmap(svg_path)
    painter = aqt.qt.QPainter(pixmap)
    painter.setCompositionMode(aqt.qt.QPainter.CompositionMode.CompositionMode_SourceIn)
    painter.fillRect(pixmap.rect(), color)
    painter.end()
    return aqt.qt.QIcon(pixmap)

def convert_company_name_to_api_key(company_name: str) -> str:
    match company_name:
        case "OpenAI":
            return "OPENAI_API_KEY"
        case "Claude":
            return "CLAUDE_API_KEY"
        case "Gemini":
            return "GEMINI_API_KEY"
        case "DeepSeek":
            return "DEEPSEEK_API_KEY"
        case _:
            return ""
