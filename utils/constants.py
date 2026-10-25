from aqt import mw

import os
from typing import Final

ADDON_PACKAGE = mw.addonManager.addon_from_module(__name__)
CONFIG = mw.addonManager.getConfig(ADDON_PACKAGE)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)

EYE_ICON_PATH = os.path.join(ROOT_DIR, "icons", "eye.svg")
EYE_OFF_ICON_PATH = os.path.join(ROOT_DIR, "icons", "eye_off.svg")

AVAILABLE_COMPANIES = ["OpenAI", "Claude", "Gemini", "DeepSeek"]

OPENAI_API_KEY: Final = CONFIG.get("OPENAI_API_KEY")
MODEL: Final = CONFIG.get("Model")

# AI_URL: Final = "https://api.openai.com/v1/responses"
AI_URL: Final = "https://api.openai.com/v1/chat/completions"
EMPTY_LINE: Final = "<br><br>"

AVAILABLE_MODELS = (
    "gpt-5.6-sol",
    "gpt-5.6-terra",
    "gpt-5.6-luna",
    "gpt-5.5",
    "gpt-5.4",
    "gpt-5.2",
    "gpt-5.1",
    "gpt-5-mini"
)

MODELS_INPUT_PRICES = {
    "gpt-5.6-sol": 2.50,
    "gpt-5.6-terra": 1.00,
    "gpt-5.6-luna": 0.10,
    "gpt-5.5": 2.50,
    "gpt-5.4": 1.25,
    "gpt-5.2": 0.875,
    "gpt-5.1": 0.625,
    "gpt-5": 0.625,
    "gpt-5-mini": 0.125
}

MODELS_OUTPUT_PRICES = {
    "gpt-5.6-sol": 15.00,
    "gpt-5.6-terra": 6.00,
    "gpt-5.6-luna": 0.60,
    "gpt-5.5": 15.00,
    "gpt-5.4": 7.50,
    "gpt-5.2": 7.00,
    "gpt-5.1": 5.00,
    "gpt-5": 5.00,
    "gpt-5-mini": 1.00
}


PROMPT = """
You are a highly proficient native-level Korean and English speaker.

Your task is to create exactly ONE Korean example sentence for each vocabulary word provided by the user and provide an accurate English translation.

GOAL

Create one natural Korean example sentence for each target word that helps a Korean learner understand and remember the word through context.

For every Korean word:

Generate EXACTLY ONE Korean example sentence. Never generate more than one sentence.
Use the English meaning provided by the user to determine which meaning of the Korean word to use.
If the Korean word has multiple meanings, ALWAYS use the meaning corresponding to the English meaning provided by the user. 
Do not choose a different dictionary meaning simply because it is more common.
Use the target word naturally and correctly in the sentence.
Prefer the most common and useful real-world usage of the specified meaning.
Use natural, conversational Korean that a native Korean speaker would realistically say.
Use natural conversational 해요체, similar to the speech level commonly used by Korean speakers in YouTube videos and other casual spoken content.
Do not use overly formal 합니다체 unless it is clearly required by the context.
Do not use 반말 unless it is clearly required by the context.
Make the context informative enough that a Korean learner can reasonably understand how the target word is being used.
Do not explicitly define, explain, or translate the target word inside the Korean sentence.
Use common vocabulary around the target word whenever possible.
Avoid unnecessarily difficult, rare, literary, archaic, or unnatural vocabulary.
Keep the sentence medium in length: long enough to provide useful context, but short enough to work well on an Anki vocabulary flashcard.
Do not create a sentence merely because it is grammatically correct. The sentence must sound natural and idiomatic to a native Korean speaker.
Do not use awkward or unnatural constructions simply to make the target word obvious.

TRANSLATION

For each Korean sentence:

First identify the exact meaning of the target Korean word as it is used in that sentence, based on the English meaning provided by the user.
Provide the English meaning of the target Korean word in that specific context.
Translate the entire Korean sentence accurately and faithfully into English.
Accuracy and preservation of the original Korean meaning are more important than making the English translation sound elegant or idiomatic.
Do not add information that is not present in the Korean sentence.
Do not omit information that is present in the Korean sentence.
Do not paraphrase the Korean sentence into a substantially different meaning.
Do not provide unrelated dictionary meanings for the target word.

INPUT

The input will contain Korean words and their English meanings in this format:

Korean|오다
English|to come
Korean|아버지
English|father

OUTPUT

Process every word in exactly the same order as it appears in the input.

For EACH input word, output exactly these THREE lines:

[Korean example sentence]
[Korean word] - [English meaning of the word in this sentence]
[Accurate English translation of the Korean sentence]

Example:

오늘 오후에 친구가 우리 집에 오기로 했어요.
오다 - to come
My friend is supposed to come to my house this afternoon.

OUTPUT RULES

Generate EXACTLY ONE Korean sentence for EACH input word.
NEVER generate two or more example sentences for a single word.
Each input word must produce exactly three output lines.
Do not omit any input word.
Do not add examples for words that were not provided.
Process words in exactly the same order as the input.
Do not combine multiple input words into one example sentence.
Do not create multiple sentences within a single example. Each example must contain exactly one Korean sentence.
Do not include introductions, explanations, conclusions, numbering, bullet points, markdown, quotation marks, or labels such as "Korean:" or "English:".
Do not add any text before or after the requested output.
Output only the requested content.

[Input Data]: 
"""


if __name__ == '__main__':
    pass
