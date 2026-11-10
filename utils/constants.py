from aqt import mw

import os
from typing import Final

ADDON_PACKAGE = mw.addonManager.addon_from_module(__name__)
CONFIG = mw.addonManager.getConfig(ADDON_PACKAGE)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)

EYE_ICON_PATH = os.path.join(ROOT_DIR, "icons", "eye.svg")
EYE_OFF_ICON_PATH = os.path.join(ROOT_DIR, "icons", "eye_off.svg")

OPENAI_ICON_PATH = os.path.join(ROOT_DIR, "icons", "openai_logo.svg")

AVAILABLE_COMPANIES = ["OpenAI"]

OPENAI_API_KEY: Final = CONFIG.get("OPENAI_API_KEY").strip()
MODEL: Final = CONFIG.get("Model")

AI_URL: Final = "https://api.openai.com/v1/chat/completions"
EMPTY_LINE: Final = "<br><br>"

AVAILABLE_MODELS = (
    "gpt-6-astra",
    "gpt-6.1-sol",
    "gpt-6.1-terra",
    "gpt-6-luna",
    "gpt-6-sol",
    "gpt-5.6-sol",
    "gpt-5.6-terra",
    "gpt-5.6-luna",
    "gpt-5.5",
    "gpt-5.4"
)

MODELS_INPUT_PRICES = {
    "gpt-6-astra": 5.00,
    "gpt-6.1-sol": 1.00,
    "gpt-6.1-terra": 0.50,
    "gpt-6-luna": 0.05,
    "gpt-6-sol": 1.00,
    "gpt-5.6-sol": 2.00,
    "gpt-5.6-terra": 1.00,
    "gpt-5.6-luna": 0.10,
    "gpt-5.5": 2.50,
    "gpt-5.4": 1.25
}

MODELS_OUTPUT_PRICES = {
    "gpt-6-astra": 25.00,
    "gpt-6.1-sol": 5.00,
    "gpt-6.1-terra": 2.50,
    "gpt-6-luna": 0.25,
    "gpt-6-sol": 5.00,
    "gpt-5.6-sol": 10.00,
    "gpt-5.6-terra": 6.00,
    "gpt-5.6-luna": 0.60,
    "gpt-5.5": 15.00,
    "gpt-5.4": 7.50
}

MAX_NOTES_TO_APPLY: Final = 30